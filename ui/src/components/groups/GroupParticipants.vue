<template>
  <div>
    <v-toolbar>
      <v-layout align-center justify-space-between fill-height>
        <v-flex md3 class="text-no-wrap">
          <v-toolbar-title v-if="!select">{{ title }}</v-toolbar-title>
          <v-toolbar-title v-else>{{ selectionOption.title }}</v-toolbar-title>
        </v-flex>
        <v-flex v-if="select" shrink>
          <v-tooltip bottom
            ><template v-slot:activator="{ on }"
              ><v-btn v-on:click="resetSelection" v-on="on" fab text>
                <v-icon dark>close</v-icon>
              </v-btn></template
            >
            {{ $t("actions.cancel") }}
          </v-tooltip>
          <v-tooltip bottom
            ><template v-slot:activator="{ on }"
              ><v-btn
                :disabled="!selectedSome"
                :loading="selectionLoading"
                color="primary"
                raised
                v-on:click="proceedSelection(selectionOption.callback)"
                v-on="on"
                fab
              >
                <v-icon dark>forward</v-icon>
              </v-btn></template
            >
            {{ $t("actions.confirm") }}
          </v-tooltip>
        </v-flex>
        <template v-if="!select">
          <v-flex md2>
            <v-text-field
              v-model="search"
              append-icon="search"
              v-bind:label="$t('actions.search')"
              single-line
              hide-details
            />
          </v-flex>
          <v-flex md1>
            <v-select
              hide-details
              solo
              single-line
              :items="viewOptions"
              v-model="viewStatus"
              data-cy="view-status-select"
            />
          </v-flex>
          <v-flex md2>
            <v-menu open-on-hover offset-y bottom>
              <template v-slot:activator="{ on }">
                <v-btn color="primary" v-on="on">
                  <v-icon>done_all</v-icon>
                  {{ $t("groups.batch-actions.title") }}
                </v-btn>
              </template>
              <v-list>
                <v-list-item @click.stop="selectionMode = 'archive'">
                  <v-icon color="primary">archive</v-icon>
                  <v-list-item-content>
                    {{ $t("groups.batch-actions.archive") }}
                  </v-list-item-content>
                </v-list-item>
                <v-list-item @click.stop="selectionMode = 'unarchive'">
                  <v-icon color="primary">redo</v-icon>
                  <v-list-item-content>
                    {{ $t("groups.batch-actions.unarchive") }}
                  </v-list-item-content>
                </v-list-item>
                <v-list-item @click.stop="selectionMode = 'email'">
                  <v-icon color="primary">email</v-icon>
                  <v-list-item-content>
                    {{ $t("groups.batch-actions.email") }}
                  </v-list-item-content>
                </v-list-item>
                <v-list-item @click.stop="showMoveDialog()">
                  <v-icon color="primary">low_priority</v-icon>
                  <v-list-item-content>
                    {{ $t("groups.batch-actions.move") }}
                  </v-list-item-content>
                </v-list-item>
                <v-list-item
                  v-if="isManagerMode"
                  @click.stop="selectionMode = 'edit'"
                >
                  <v-icon color="primary">edit</v-icon>
                  <v-list-item-content>
                    {{ $t("groups.batch-actions.edit") }}
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-flex>
          <v-flex shrink justify-self-end>
            <v-btn
              color="primary"
              raised
              :disabled="select"
              v-on:click="showParticipantDialog()"
              data-cy="add-participant"
            >
              <v-icon dark left>add</v-icon>
              {{
                isManagerMode
                  ? $t("groups.managers.add-manager")
                  : $t("groups.members.add-member")
              }}
            </v-btn>
          </v-flex>
        </template>
      </v-layout>
    </v-toolbar>
    <v-data-table
      v-model="selected"
      :items-per-page-options="itemsPerPageOptions"
      :headers="headers"
      :items="visibleParticipants"
      :show-select="select"
      item-key="person.id"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
      :footer-props='{itemsPerPageText: $t("$vuetify.dataTable.rowsPerPageText")}'
    >
      <template v-slot:header.data-table-select>
        <v-simple-checkbox
          color="primary"
          :value="selectedAll"
          :indeterminate="selectedIndeterminate"
          hide-details
          @click.stop="toggleAll"
        />
      </template>
      <template v-slot:item.data-table-select="props">
        <v-tooltip :disabled="!props.item.disabled" right>
          <!-- show tooltip when the item is disabled -->
          <template v-slot:activator="{ on }">
            <span class="d-inline-block" v-on="on">
              <v-simple-checkbox
                @click.stop="toggleSelect(props)"
                color="primary"
                :value="props.isSelected"
                :disabled="props.item.disabled"
              />
            </span>
          </template>
          {{ props.item.disabledText }}
        </v-tooltip>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-tooltip v-for="action in actions" :key="action.key" bottom>
          <template v-slot:activator="{ on }"
            ><v-btn
              v-on="on"
              icon
              outlined
              small
              color="primary"
              :disabled="select"
              v-if="!action.show || action.show(item)"
              :loading="action.loading && action.loading(item)"
              v-on:click="action.clickHandler && action.clickHandler(item)"
              data-cy="action.key"
              v-bind="action.attrs"
            >
              <v-icon small>{{ action.icon }}</v-icon>
            </v-btn></template
          >
          <span>{{ action.tooltipText }}</span>
        </v-tooltip>
      </template>
      <template v-slot:footer.page-text="items"> {{ items.pageStart }} - {{ items.pageStop }} of {{ items.itemsLength }} </template>
    </v-data-table>

    <!-- Archive dialog -->
    <v-dialog v-model="archiveDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{
          isManagerMode
            ? $t("groups.messages.confirm-manager-archive")
            : $t("groups.messages.confirm-member-archive")
        }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="hideArchiveDialog"
            color="secondary"
            text
            data-cy="cancel-archive"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer />
          <v-btn
            v-on:click="archiveParticipants(archiveDialog.participants)"
            color="primary"
            raised
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Participant Dialog -->
    <v-dialog v-model="participantDialog.show" max-width="350px" persistent>
      <v-card>
        <v-card-title primary-title>
          <div>
            <h3 v-if="participantDialog.editMode" class="headline mb-0">
              {{
                isManagerMode
                  ? $t("groups.managers.edit-manager")
                  : $t("groups.members.edit-member")
              }}
            </h3>
            <h3 v-else class="headline mb-0">
              {{
                isManagerMode
                  ? $t("groups.managers.add-manager")
                  : $t("groups.members.add-member")
              }}
            </h3>
          </div>
        </v-card-title>
        <v-card-text>
          <entity-search
            multiple
            person
            v-model="participantDialog.persons"
            :existing-entities="persons"
            :disabled="participantDialog.editMode"
          />
          <entity-type-form
            v-if="isManagerMode"
            entity-type-name="manager"
            v-model="participantDialog.participantType"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn v-on:click="hideParticipantDialog" color="secondary" text>{{
            $t("actions.cancel")
          }}</v-btn>
          <v-spacer />
          <v-btn
            v-on:click="confirmParticipantDialog"
            :disabled="participantDialog.persons.length === 0"
            color="primary"
            raised
            :loading="participantDialog.loading"
            >{{ $t("actions.save") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Email dialog -->
    <v-dialog v-model="emailDialog.show" max-width="700px">
      <email-form
        :initialData="emailDialog.initialData"
        @sent="hideEmailDialog"
        @error="hideEmailDialog"
        @cancel="hideEmailDialog"
      />
    </v-dialog>

    <!-- Move dialog -->
    <v-dialog v-model="moveDialog.show" max-width="350px">
      <v-card>
        <v-card-title primary-title>
          <span class="headline">
            {{ $t("groups.messages.select-destination-group") }}
          </span>
        </v-card-title>
        <v-card-text>
          <v-chip v-if="moveDialog.participant"
            ><v-icon>person</v-icon
            >{{ moveDialog.participant.person.firstName }}
            {{ moveDialog.participant.person.lastName }}</v-chip
          >
          <entity-search
            group
            :label="$t('groups.messages.select-destination-group')"
            v-model="moveDialog.destinationGroup"
            :existing-entities="invalidDestinationGroups"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn v-on:click="hideMoveDialog" color="secondary" text>{{
            $t("actions.cancel")
          }}</v-btn>
          <v-spacer />
          <v-btn
            v-on:click="confirmMoveDialog"
            :disabled="isEmpty(moveDialog.destinationGroup)"
            color="primary"
            raised
            >{{ $t("actions.continue") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import EntitySearch from "../EntitySearch";
import EmailForm from "../EmailForm";
import EntityTypeForm from "./EntityTypeForm";
import { eventBus } from "../../plugins/event-bus.js";
import { isEmpty } from "lodash";
export default {
  components: { EntitySearch, EmailForm, EntityTypeForm },
  name: "GroupParticipants",
  props: {
    participantType: {
      /* either 'manager' or 'member' */
      type: String,
      default: "manager",
    },
  },

  data() {
    return {
      itemsPerPageOptions: [
        10,
        15,
        25,
        { text: "$vuetify.dataIterator.rowsPerPageAll", value: -1 },
      ],
      tableLoading: false,
      search: "",
      participants: [],
      selected: [],
      emailDialog: {
        show: false,
        loading: false,
        initialData: {
          recipients: [],
          recipientList: [],
        },
      },
      participantDialog: {
        show: false,
        persons: [],
        participantType: {},
        editMode: false,
        loading: false,
      },
      archiveDialog: {
        show: false,
        participants: [],
        loading: false,
      },
      moveDialog: {
        /* if not empty, confirm on moveDialog will move this participant directly
        instead of activating selection mode */
        participant: null,
        loading: false,
        show: false,
        destinationGroup: {},
      },
      viewStatus: "viewActive",
      selectionMode: "noSelect",
      selectionLoading: false,
    };
  },

  computed: {
    /************* general computed properties ****************/
    viewOptions() {
      return [
        { text: this.$t("actions.view-active"), value: "viewActive" },
        { text: this.$t("actions.view-archived"), value: "viewArchived" },
        { text: this.$t("actions.view-all"), value: "viewAll" },
      ];
    },
    title() {
      return this.isManagerMode
        ? this.$t("groups.header-manager")
        : this.$t("events.participants.title");
    },
    headers() {
      let headers = [
        {
          text: this.$t("person.name.first"),
          value: "person.firstName",
        },
        {
          text: this.$t("person.name.last"),
          value: "person.lastName",
        },
        {
          text: this.$t("person.email"),
          value: "person.email",
        },
        {
          text: this.$t("actions.header"),
          value: "actions", // does not exist, used to identify the actions column
          sortable: false,
        },
      ];
      if (this.isManagerMode) {
        headers.splice(3, 0, {
          text: this.$t("groups.managers.manager-type"),
          value: "managerType.name",
        });
      }
      return headers;
    },
    actions() {
      return [
        {
          key: "edit",
          icon: "edit",
          tooltipText: this.$t("actions.edit"),
          show: (item) => item.active && this.isManagerMode,
          clickHandler: (item) => this.showParticipantDialog([item]),
          attrs: {}, // additional attributes here
        },
        {
          key: "archive",
          icon: "archive",
          tooltipText: this.$t("actions.tooltips.archive"),
          show: (item) => item.active,
          clickHandler: (item) => this.showArchiveDialog([item]),
        },
        {
          key: "move",
          icon: "low_priority",
          tooltipText: this.$t("actions.tooltips.move"),
          show: (item) => item.active,
          clickHandler: (item) => this.showMoveDialog(item),
        },
        {
          key: "email",
          icon: "email",
          tooltipText: this.$t("actions.tooltips.email"),
          show: (item) => item.active && item.person.email,
          clickHandler: (item) => this.showEmailDialog([item]),
        },
        {
          key: "unarchive",
          icon: "undo",
          tooltipText: this.$t("actions.tooltips.activate"),
          show: (item) => !item.active,
          clickHandler: (item) => this.unarchiveParticipant(item),
          loading: (item) => item.id < 0,
        },
      ];
    },
    id() {
      return parseInt(this.$route.params.group);
    },
    isManagerMode() {
      return this.participantType === "manager";
    },
    endpoint() {
      return `/api/v1/groups/groups/${this.id}/${
        this.isManagerMode ? "managers" : "members"
      }`;
    },

    /************* selection helper properties ****************/
    select() {
      return this.selectionMode !== "noSelect";
    },
    selectable() {
      return this.visibleParticipants.filter((p) => !p.disabled);
    },
    selectedSome() {
      return this.selected.length !== 0;
    },
    selectedAll() {
      return (
        this.selectedSome && this.selected.length === this.selectable.length
      );
    },
    selectedIndeterminate() {
      return this.selectedSome && !this.selectedAll;
    },
    selectionOptions() {
      return {
        /* options to be defined for each selectionMode */
        archive: {
          title: this.$t("groups.batch-actions.archive"), // the title to be displayed in selection mode
          callback: this.showArchiveDialog, // a callback function that takes the selected items as parameter
        },
        unarchive: {
          title: this.$t("groups.batch-actions.unarchive"),
          callback: this.unarchiveParticipants,
        },
        email: {
          title: this.$t("groups.batch-actions.email"),
          callback: this.showEmailDialog,
        },
        move: {
          title: this.$t("groups.batch-actions.move"),
          callback: this.batchMoveParticipants,
        },
        edit: {
          title: this.$t("groups.batch-actions.edit"),
          callback: this.showParticipantDialog,
        },
      };
    },
    selectionOption() {
      let { [this.selectionMode]: option } = this.selectionOptions;
      return option;
    },

    /************* filters ****************/
    activeParticipants() {
      return this.participants.filter((p) => p.active);
    },
    inactiveParticipants() {
      return this.participants.filter((p) => !p.active);
    },
    persons() {
      return this.participants.map((m) => m.person);
    },
    selectionArchiveParticipants() {
      return this.activeParticipants;
    },
    selectionUnarchiveParticipants() {
      return this.inactiveParticipants;
    },
    selectionEmailParticipants() {
      return this.activeParticipants.map((p) => ({
        disabled: !p.person.email,
        disabledText: this.$t("groups.batch-actions.messages.no-email"),
        ...p,
      }));
    },
    selectionMoveParticipants() {
      /* TODO: also filter out movements that will
      create a cycle in the leadership hierarchy <2020-07-01, David Deng> */
      let destinationGroupPersonIds = this.moveDialog.destinationGroup[
        this.isManagerMode ? "managers" : "members"
      ].map((p) => p.person.id);
      let movableParticipants = this.activeParticipants.map((p) => {
        let participant = { ...p };
        if (destinationGroupPersonIds.includes(p.person.id)) {
          participant.disabled = true;
          participant.disabledText = this.$t(
            "groups.batch-actions.messages.person-in-destination-group"
          );
        } // else if (moving participant will create cycle) {...}
        return participant;
      });
      return movableParticipants;
    },
    selectionEditParticipants() {
      return this.activeParticipants;
    },
    visibleParticipants() {
      if (this.select) {
        // selection mode
        if (this.selectionMode === "archive") {
          return this.selectionArchiveParticipants;
        } else if (this.selectionMode === "unarchive") {
          return this.selectionUnarchiveParticipants;
        } else if (this.selectionMode === "email") {
          return this.selectionEmailParticipants;
        } else if (this.selectionMode === "move") {
          return this.selectionMoveParticipants;
        } else if (this.selectionMode === "edit") {
          return this.selectionEditParticipants;
        } else {
          console.error(`${this.selectionMode} is not a valid selection mode`);
          return this.participants;
        }
      } else {
        // not in selection mode
        if (this.viewStatus === "viewActive") {
          return this.activeParticipants;
        } else if (this.viewStatus === "viewArchived") {
          return this.inactiveParticipants;
        } else {
          return this.participants;
        }
      }
    },
    /* all possible recipient */
    emailRecipientList() {
      return this.participants
        .filter((m) => m.person.email && m.active)
        .map((m) => ({
          email: m.person.email,
          name: `${m.person.firstName} ${m.person.lastName}`,
        }));
    },
    invalidDestinationGroups() {
      let groups = [{ id: this.id }]; // cannot move to the current group
      if (this.moveDialog.participant) {
        // also exclude groups that the participant is in
        groups = groups.concat(
          this.moveDialog.participant.person[
            this.isManagerMode ? "managers" : "members"
          ].map((m) => ({ id: m.groupId }))
        );
      }
      return groups;
    },
  },

  methods: {
    /************* general ****************/
    isEmpty,

    /************* selection helper methods ****************/
    proceedSelection(callback) {
      this.selectionLoading = true;
      Promise.resolve(callback([...this.selected])).then(() => {
        this.selectionLoading = false;
        this.resetSelection();
      });
    },
    resetSelection() {
      this.selectionMode = "noSelect";
      this.selected = [];
    },
    toggleSelect(props) {
      if (this.select && !props.item.disabled) {
        props.select(!props.isSelected);
      }
    },
    toggleAll() {
      if (!this.selectedAll) {
        this.selected = this.selectable;
      } else {
        this.selected = [];
      }
    },

    /************* dialog helper methods ****************/
    showParticipantDialog(participants) {
      if (participants) {
        this.participantDialog.editMode = true;
        this.participantDialog.persons = participants.map((m) => m.person);
      } else {
        this.participantDialog.editMode = false;
        this.participantDialog.persons = [];
      }
      this.participantDialog.show = true;
    },
    hideParticipantDialog() {
      this.participantDialog.show = false;
    },
    confirmParticipantDialog() {
      if (editMode && !this.isManagerMode) {
        // ui should hide buttons as appropriate to prevent this case
        console.error("There is nothing to edit for members");
        return;
      }
      let editMode = this.participantDialog.editMode;
      this.participantDialog.loading = true;
      let payload = {};
      if (this.isManagerMode) {
        payload.managerTypeId = this.participantDialog.participantType.id;
      if (editMode) {
        if (!this.isManagerMode) {
          // ui should hide buttons as appropriate to prevent this case
          console.error("There is nothing to edit for members");
          return;
        }
      }
      this.saveParticipants(
        this.participantDialog.persons,
        editMode ? "patch" : "post",
        payload
      )
        .then(() => {
          this.fetchParticipants();
          eventBus.$emit("message", {
            content: editMode
              ? this.isManagerMode
                ? "groups.messages.managers-updated"
                : "groups.messages.members-updated"
              : this.isManagerMode
              ? "groups.messages.managers-added"
              : "groups.messages.members-added",
          });
        })
        .catch((err) => {
          console.log(err);
          eventBus.$emit("error", {
            content: editMode
              ? this.isManagerMode
                ? "groups.messages.error-updating-managers"
                : "groups.messages.error-updating-members"
              : this.isManagerMode
              ? "groups.messages.error-adding-managers"
              : "groups.messages.error-adding-members",
          });
        })
        .finally(() => {
          this.participantDialog.loading = false;
          this.hideParticipantDialog();
        });
      }
      },
    showEmailDialog(participants) {
      let recipients = participants.map((participant) => ({
        email: participant.person.email,
        name: `${participant.person.firstName} ${participant.person.lastName}`,
      }));
      this.emailDialog.initialData.recipients = recipients;
      this.emailDialog.initialData.recipientList = this.emailRecipientList;
      this.emailDialog.show = true;
    },
    hideEmailDialog() {
      this.emailDialog.show = false;
    },
    showArchiveDialog(participants) {
      this.archiveDialog.participants = participants;
      this.archiveDialog.show = true;
    },
    hideArchiveDialog() {
      this.archiveDialog.show = false;
    },
    showMoveDialog(participant = null) {
      this.moveDialog.participant = participant;
      this.moveDialog.destinationGroup = {};
      this.moveDialog.show = true;
    },
    hideMoveDialog() {
      this.moveDialog.show = false;
    },
    confirmMoveDialog() {
      if (this.moveDialog.participant) {
        // if participants already known
        this.moveDialog.loading = true;
        this.batchMoveParticipants([this.moveDialog.participant]).finally(
          () => {
            this.moveDialog.loading = false;
            this.hideMoveDialog();
          }
        );
      } else {
        // go to select view
        this.hideMoveDialog();
        this.selectionMode = "move";
      }
    },
    batchMoveParticipants(participants) {
      return this.saveParticipants(
        participants.map((p) => p.person),
        {
          groupId: this.moveDialog.destinationGroup.id,
        }
      )
        .then(() => {
          this.fetchParticipants();
          eventBus.$emit("message", {
            content: this.isManagerMode
              ? "groups.messages.managers-moved"
              : "groups.messages.members-moved",
          });
        })
        .catch((err) => {
          console.log(err);
          eventBus.$emit("error", {
            content: this.isManagerMode
              ? "groups.messages.error-moving-managers"
              : "groups.messages.error-moving-members",
          });
        });
    },

    /************* api methods ****************/
    /* add or update the participants associated with current group and each person in 'persons',
    'method' is a string either being 'patch' or 'post', specifying whether to add or update the participants
    'payload' is a dictionary specifying additional attributes (e.g. managerTypeId) to be used in the request payload */
    saveParticipants(persons, method, payload = {}) {
      let promises = [];
      let http = this.$http[method];
      let endpoint = this.endpoint;
      for (let person of persons) {
        if (method === "post") {
          // if adding participants
          payload.personId = person.id;
        } else if (method === "patch") {
          // if updating participants
          endpoint = `${endpoint}/${person.id}`;
        }
        promises.push(http(endpoint, payload, { noErrorSnackBar: true }));
      }
      return Promise.all(promises);
    },
    /* archive or unarchive the participants */
    archiveParticipants(participants, unarchive = false) {
      let promises = [];
      this.archiveDialog.loading = true;
      for (let participant of participants) {
        promises.push(
          this.$http.patch(
            `${this.endpoint}/${participant.person.id}`,
            { active: unarchive ? true : false },
            { noErrorSnackBar: true }
          )
        );
      }
      return Promise.all(promises)
        .then(() => {
          this.fetchParticipants();
          eventBus.$emit("message", {
            content: "groups.messages.member-archived",
          });
        })
        .catch((err) => {
          console.error("PATCH ERROR", err);
          eventBus.$emit("error", {
            content: "groups.messages.error-archiving-member",
          });
        })
        .finally(() => {
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
        });
    },
    unarchiveParticipants(participants) {
      return this.archiveParticipants(participants, true);
    },
    unarchiveParticipant(participant) {
      const participantId = participant.id;
      participant.id = -1; // show loading state
      this.archiveParticipants([participant], true).finally(() => {
        participant.id = participantId;
      });
    },
    fetchParticipants() {
      this.tableLoading = true;
      this.$http.get(this.endpoint).then((resp) => {
        this.participants = resp.data;
        console.log(resp.data);
        this.tableLoading = false;
      });
    },
  },
  mounted() {
    this.fetchParticipants();
  },
};
</script>

<style>
.v-icon {
  display: inline-flex !important;
}
</style>
