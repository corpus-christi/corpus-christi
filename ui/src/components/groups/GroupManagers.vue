<template>
  <div>
    <v-toolbar>
      <v-layout align-center justify-space-between fill-height>
        <v-flex md3 class="text-no-wrap">
          <v-toolbar-title v-if="!select">{{ title }}</v-toolbar-title>
          <v-btn
            color="primary"
            raised
            v-on:click="showEmailDialog"
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
            v-on:click="openParticipantDialog"
            data-cy="add-participant"
          >
            <v-icon dark left>add</v-icon>
            {{ $t("actions.add-manager") }}
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
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="editPerson(props.item.person)"
                data-cy="edit"
              >
                <v-icon small>edit</v-icon>
              </v-btn>
              <span>{{ $t("actions.edit") }}</span>
            </v-tooltip>
          </template>
          <template v-if="props.item.active">
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
          </template>
          <template v-else>
            <v-tooltip bottom v-if="!props.item.active">
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
            v-on:click="massArchive()"
            color="primary"
            raised
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Add Participant Dialog -->
    <v-dialog v-model="addParticipantDialog.show" max-width="350px">
      <v-card>
        <v-card-title primary-title>
          <div>
            <h3 class="headline mb-0">
              {{ $t("person.actions.add-manager") }}
            </h3>
          </div>
        </v-card-title>
        <v-card-text>
          <entity-search
            multiple
            person
            v-model="addParticipantDialog.newParticipants"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelNewParticipantDialog"
            color="secondary"
            flat
            data-cy=""
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer />
          <v-btn
            v-on:click="addParticipants"
            :disabled="addParticipantDialog.newParticipants.length === 0"
            color="primary"
            raised
            :loading="addParticipantDialog.loading"
            data-cy="confirm-participant"
            >{{ $t("actions.add-manager") }}</v-btn
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

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false">
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>
  </div>
</template>

<script>
import EntitySearch from "../EntitySearch";
import EmailForm from "../EmailForm";
import { eventBus } from "../../plugins/event-bus.js";
export default {
  components: { EntitySearch, EmailForm },
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
      select: false,
      unarchiveSelect: false,
      emailDialog: {
        show: false,
        loading: false
      },
      addParticipantDialog: {
        show: false,
        newParticipants: [],
        loading: false
      },
      archiveDialog: {
        show: false,
        participants: [],
        loading: false
      },
      snackbar: {
        show: false,
        text: ""
      },
      viewStatus: "viewActive"
    };
  },

  watch: {
    selected() {
      if (this.selected.length > 0) {
        this.select = true;
      } else this.select = false;
    }
  },

  computed: {
    id() {
      return this.$route.params.group;
    },
    isManagerMode() {
      return this.participantType == "manager";
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
    emailRecipients() {
      return this.selected
        .filter(m => m.person.email)
        .map(m => ({
          email: m.person.email,
          name: `${m.person.firstName} ${m.person.lastName}`
        }));
    },
    emailRecipientList() {
      return this.participants
        .filter(m => m.person.email)
        .map(m => ({
          email: m.person.email,
          name: `${m.person.firstName} ${m.person.lastName}`
        }));
    },
    emailInitialData() {
      return {
        recipients: this.emailRecipients,
        recipientList: this.emailRecipientList
      };
    }
  },

  methods: {
    activateNewParticipantDialog() {
      this.addParticipantDialog.show = true;
    },

    openParticipantDialog() {
      this.activateNewParticipantDialog();
    },

    cancelNewParticipantDialog() {
      this.addParticipantDialog.show = false;
    },

    editPerson(person) {
      this.dialogState = "edit";
    },

    cancelPerson() {
      this.dialogState = "";
    },

    addParticipants() {
      this.addParticipantDialog.loading = true;
      let promises = [];

      for (let person of this.addParticipantDialog.newParticipants) {
        const idx = this.participants.findIndex(
          gr_pe => gr_pe.person.person_id === person.id
        );
        if (idx === -1) {
          promises.push(this.addParticipant(person.id));
        }
      }

      Promise.all(promises)
        .then(() => {
          this.addParticipantDialog.loading = false;
          this.addParticipantDialog.show = false;
          this.addParticipantDialog.newParticipants = [];
          this.getParticipants();
          eventBus.$emit("message", {
            content: "groups.messages.members-added"
          });
        })
        .catch(err => {
          console.log(err);
          this.addParticipantDialog.loading = false;
          eventBus.$emit("error", {
            content: "groups.messages.error-adding-members"
          });
        });
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

    showEmailDialog() {
      this.emailDialog.show = true;
    },
    hideEmailDialog() {
      this.emailDialog.show = false;
    },

    addParticipant(id) {
      for (var member of this.participants) {
        if (this.id == member.person.id) {
          return true;
        }
      }
      return this.$http.post(`/api/v1/groups/groups/${this.id}/managers`, {
        personId: id,
        managerTypeId: 1
      });
    },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },
    massArchive(unarchive = false) {
      let promises = [];
      this.archiveDialog.loading = true;
      console.log(this.archiveDialog.participants);
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
              `/api/v1/groups/groups/${this.id}/${
                this.isManagerMode ? "managers" : "members"
              }/${participant.person.id}`,
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
      this.massArchive(true);
    },
    unarchiveParticipant(participant) {
      this.archiveDialog.participants = [participant];
      this.massArchive(true);
    },
    getParticipants() {
      this.tableLoading = true;
      this.$http
        .get(
          `/api/v1/groups/groups/${this.id}/${
            this.isManagerMode ? "managers" : "members"
          }`
        )
        .then(resp => {
          this.participants = resp.data;
          console.log(resp.data);
          this.tableLoading = false;
        });
    }
  },
  mounted: function() {
    this.getParticipants();
  }
};
</script>

<style>
.v-icon {
  display: inline-flex !important;
}
</style>
