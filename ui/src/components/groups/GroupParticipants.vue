<template>
  <div>
    <v-toolbar>
      <v-layout align-center justify-space-between fill-height>
        <v-flex md3 class="text-no-wrap">
          <v-toolbar-title v-if="!select">{{ title }}</v-toolbar-title>
          <v-btn
            color="primary"
            raised
            v-on:click="showParticipantDialog"
            v-if="select && isManagerMode"
            fab
            small
          >
            <v-icon dark>edit</v-icon>
          </v-btn>
          <v-btn
            color="primary"
            raised
            v-on:click="showSelectEmailDialog"
            v-if="select"
            fab
            small
          >
            <v-icon dark>email</v-icon>
          </v-btn>
          <v-btn
            color="primary"
            raised
            v-on:click="showSelectArchiveDialog"
            data-cy="archive"
            v-if="select"
            fab
            small
          >
            <v-icon dark>archive</v-icon>
          </v-btn>
          <v-btn
            color="primary"
            raised
            v-on:click="unarchiveSelected"
            v-if="select"
            fab
            small
          >
            <v-icon dark>undo</v-icon>
          </v-btn>
        </v-flex>
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
          >
          </v-select>
        </v-flex>
        <v-flex shrink justify-self-end>
          <v-btn
            color="primary"
            raised
            v-on:click="showParticipantDialog"
            data-cy="add-participant"
          >
            <v-icon dark left>add</v-icon>
            {{ isManagerMode ? $t("actions.add-manager") : "Add Members" }}
          </v-btn>
        </v-flex>
      </v-layout>
    </v-toolbar>
    <v-data-table
      select-all
      v-model="selected"
      :rows-per-page-items="rowsPerPageItem"
      :headers="headers"
      :items="visibleParticipants"
      item-key="person.id"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td><v-checkbox v-model="props.selected" primary hide-details /></td>
        <td>{{ props.item.person.firstName }}</td>
        <td>{{ props.item.person.lastName }}</td>
        <td>{{ props.item.person.email }}</td>
        <td v-if="isManagerMode">{{ props.item.managerType.name }}</td>
        <td class="text-no-wrap">
          <template v-if="props.item.active">
            <v-tooltip bottom>
              <v-btn
                v-if="isManagerMode"
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="editParticipant(props.item)"
                data-cy="edit"
              >
                <v-icon small>edit</v-icon>
              </v-btn>
              <span>{{ $t("actions.edit") }}</span>
            </v-tooltip>
            <v-tooltip bottom>
              <v-btn
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="showArchiveDialog(props.item)"
                data-cy="archive"
              >
                <v-icon small>archive</v-icon>
              </v-btn>
              <span>{{ $t("actions.tooltips.archive") }}</span>
            </v-tooltip>
            <v-tooltip bottom>
              <v-btn
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="showEmailDialog(props.item)"
                data-cy="email"
              >
                <v-icon small>email</v-icon>
              </v-btn>
              <span>{{ $t("actions.tooltips.email") }}</span>
            </v-tooltip>
          </template>
          <template v-else>
            <v-tooltip bottom>
              <v-btn
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="unarchiveParticipant(props.item)"
                :loading="props.item.id < 0"
                data-cy="unarchive"
              >
                <v-icon small>undo</v-icon>
              </v-btn>
              <span>{{ $t("actions.tooltips.activate") }}</span>
            </v-tooltip>
          </template>
        </td>
      </template>
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
            flat
            data-cy="cancel-archive"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer />
          <v-btn
            v-on:click="archiveParticipants()"
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
    <v-dialog v-model="participantDialog.show" max-width="350px">
      <v-card>
        <v-card-title primary-title>
          <div>
            <h3 v-if="isManagerMode" class="headline mb-0">
              {{
                participantDialog.editMode
                  ? "Edit Manager"
                  : $t("person.actions.add-manager")
              }}
            </h3>
            <h3 v-else class="headline mb-0">
              {{ participantDialog.editMode ? "Edit Member" : "Add Member" }}
            </h3>
          </div>
        </v-card-title>
        <v-card-text>
          <entity-search
            multiple
            person
            v-model="participantDialog.participants"
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
          <v-btn v-on:click="hideParticipantDialog" color="secondary" flat>{{
            $t("actions.cancel")
          }}</v-btn>
          <v-spacer />
          <v-btn
            v-on:click="updateParticipants"
            :disabled="participantDialog.participants.length === 0"
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
        :initialData="emailInitialData"
        @sent="handleEmailSent"
        @error="handleEmailError"
        @cancel="handleEmailCancel"
      ></email-form>
    </v-dialog>
  </div>
</template>

<script>
import EntitySearch from "../EntitySearch";
import EmailForm from "../EmailForm";
import EntityTypeForm from "./EntityTypeForm";
import { eventBus } from "../../plugins/event-bus.js";
export default {
  components: { EntitySearch, EmailForm, EntityTypeForm },
  name: "GroupParticipants",
  props: {
    participantType: {
      /* either 'manager' or 'member' */
      type: String,
      default: "manager"
    }
  },
  data() {
    return {
      rowsPerPageItem: [
        10,
        15,
        25,
        { text: "$vuetify.dataIterator.rowsPerPageAll", value: -1 }
      ],
      tableLoading: false,
      dialogState: "",
      search: "",
      participants: [],
      people: [],
      selected: [],
      unarchiveSelect: false,
      emailDialog: {
        show: false,
        loading: false
      },
      emailInitialData: {
        recipients: [],
        recipientList: []
      },
      participantDialog: {
        show: false,
        participants: [],
        participantType: {},
        editMode: false,
        loading: false
      },
      archiveDialog: {
        show: false,
        participants: [],
        loading: false
      },
      viewStatus: "viewActive"
    };
  },

  computed: {
    id() {
      return this.$route.params.group;
    },
    isManagerMode() {
      return this.participantType == "manager";
    },
    endpoint() {
      return `/api/v1/groups/groups/${this.id}/${
        this.isManagerMode ? "managers" : "members"
      }`;
    },
    select() {
      return this.selected.length > 0;
    },
    viewOptions() {
      return [
        { text: this.$t("actions.view-active"), value: "viewActive" },
        { text: this.$t("actions.view-archived"), value: "viewArchived" },
        { text: this.$t("actions.view-all"), value: "viewAll" }
      ];
    },
    title() {
      return this.isManagerMode
        ? this.$t("groups.header-manager")
        : this.$t("events.participants.title");
    },
    headers() {
      if (this.isManagerMode) {
        return [
          {
            text: this.$t("person.name.first"),
            value: "person.firstName"
          },
          {
            text: this.$t("person.name.last"),
            value: "person.lastName"
          },
          {
            text: this.$t("person.email"),
            value: "person.email"
          },
          {
            text: this.$t("person.manager-type"),
            value: "person.manager-type"
          },
          {
            text: this.$t("actions.header"),
            sortable: false
          }
        ];
      } else {
        return [
          {
            text: this.$t("person.name.first"),
            value: "person.firstName"
          },
          {
            text: this.$t("person.name.last"),
            value: "person.lastName"
          },
          {
            text: this.$t("person.email"),
            value: "person.email"
          },
          {
            text: this.$t("actions.header"),
            sortable: false
          }
        ];
      }
    },
    persons() {
      return this.participants.map(m => m.person);
    },
    visibleParticipants() {
      let list = this.participants;

      if (this.viewStatus === "viewActive") {
        return list.filter(ev => ev.active);
      } else if (this.viewStatus === "viewArchived") {
        return list.filter(ev => !ev.active);
      } else {
        return list;
      }
    },
    selectedEmailRecipients() {
      return this.selected
        .filter(m => m.person.email)
        .map(m => ({
          email: m.person.email,
          name: `${m.person.firstName} ${m.person.lastName}`
        }));
    },
    /* all possible recipient */
    emailRecipientList() {
      return this.participants
        .filter(m => m.person.email)
        .map(m => ({
          email: m.person.email,
          name: `${m.person.firstName} ${m.person.lastName}`
        }));
    }
  },

  methods: {
    editParticipant(participant) {
      this.participantDialog.editMode = true;
      this.participantDialog.participants = [participant.person];
      this.participantDialog.show = true;
    },
    showParticipantDialog() {
      if (this.select) {
        this.participantDialog.editMode = true;
        this.participantDialog.participants = this.selected.map(m => m.person);
      } else {
        this.participantDialog.editMode = false;
        this.participantDialog.participants = [];
      }
      this.participantDialog.show = true;
    },
    hideParticipantDialog() {
      this.participantDialog.show = false;
    },

    handleEmailSent() {
      this.hideEmailDialog();
    },
    handleEmailCancel() {
      this.hideEmailDialog();
    },
    handleEmailError() {
      this.hideEmailDialog();
    },

    /* FIXME: currently can't pass the appropriate emails to the email dialog */
    showEmailDialog(participant) {
      let recipient = {
        email: participant.person.email,
        name: `${participant.person.firstName} ${participant.person.lastName}`
      };
      this.emailInitialData.recipients = [recipient];
      this.emailInitialData.recipientList = this.emailRecipientList;
      this.emailDialog.show = true;
    },
    hideEmailDialog() {
      this.emailDialog.show = false;
    },
    showSelectEmailDialog() {
      this.emailInitialData.recipients = this.selectedEmailRecipients;
      this.emailInitialData.recipientList = this.emailRecipientList;
      this.emailDialog.show = true;
    },

    /* add or update the persons in this.participantDialog.participants,
       if isManagerMode, the added managers will be set to this.participantDialog.participantType */
    updateParticipants() {
      if (this.participantDialog.editMode && !this.isManagerMode) {
        // ui should hide buttons as appropriate to prevent this case
        console.error("There is nothing to edit for members");
        return;
      }
      this.participantDialog.loading = true;
      let promises = [];
      for (let person of this.participantDialog.participants) {
        let payload = {};
        let endpoint = this.endpoint;
        let method = this.$http.post;
        if (this.participantDialog.editMode) {
          endpoint = `${endpoint}/${person.id}`;
          method = this.$http.patch;
          console.log(endpoint);
        } else {
          payload.personId = person.id;
        }
        if (this.isManagerMode) {
          payload.managerTypeId = this.participantDialog.participantType.id;
        }
        promises.push(method(endpoint, payload, { noErrorSnackBar: true }));
      }
      Promise.all(promises)
        .then(() => {
          this.participantDialog.loading = false;
          this.participantDialog.show = false;
          this.getParticipants();
          eventBus.$emit("message", {
            content: "groups.messages.members-added"
          });
        })
        .catch(err => {
          console.log(err);
          this.participantDialog.loading = false;
          eventBus.$emit("error", {
            content: "groups.messages.error-adding-members"
          });
        });
    },

    /* archive or unarchive the participants in this.archiveDialog.participants */
    archiveParticipants(unarchive = false) {
      let promises = [];
      this.archiveDialog.loading = true;
      for (let participant of this.archiveDialog.participants) {
        const participantObj = this.participants.find(
          p => p.person.id === participant.person.id
        );
        if (
          (!unarchive && participantObj && participantObj.active) ||
          (unarchive && participantObj && !participantObj.active)
        ) {
          // in archive mode, we want to pick active ones among the given participants, and vise versa.
          promises.push(
            this.$http.patch(
              `${this.endpoint}/${participant.person.id}`,
              { active: unarchive ? true : false },
              { noErrorSnackBar: true }
            )
          );
        }
      }
      if (promises.length == 0) {
        eventBus.$emit("notification", {
          content: unarchive
            ? "groups.messages.error-archived-not-selected"
            : "groups.messages.error-active-not-selected"
        });
        this.archiveDialog.loading = false;
        return;
      }
      Promise.all(promises)
        .then(resp => {
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          this.getParticipants();
          eventBus.$emit("message", {
            content: "groups.messages.member-archived"
          });
        })
        .catch(err => {
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          eventBus.$emit("error", {
            content: "groups.messages.error-archiving-member"
          });
        });
    },
    showSelectArchiveDialog() {
      this.archiveDialog.participants = this.selected;
      this.archiveDialog.show = true;
    },
    showArchiveDialog(participant) {
      this.archiveDialog.participants = [participant];
      this.archiveDialog.show = true;
    },
    hideArchiveDialog() {
      this.archiveDialog.show = false;
    },
    unarchiveSelected() {
      this.archiveDialog.participants = this.selected;
      this.archiveParticipants(true);
    },
    unarchiveParticipant(participant) {
      this.archiveDialog.participants = [participant];
      this.archiveParticipants(true);
    },
    getParticipants() {
      this.tableLoading = true;
      this.$http.get(this.endpoint).then(resp => {
        this.participants = resp.data;
        console.log(resp.data);
        this.tableLoading = false;
      });
    }
  },
  mounted() {
    this.getParticipants();
  }
};
</script>

<style>
.v-icon {
  display: inline-flex !important;
}
</style>
