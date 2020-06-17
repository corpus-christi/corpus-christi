<template>
  <div>
    <v-toolbar>
      <v-layout align-center justify-space-between fill-height>
        <v-flex md3 class="text-no-wrap">
          <v-toolbar-title v-if="!select">{{
            $t("events.participants.title")
          }}</v-toolbar-title>
          <v-btn
            color="primary"
            raised
            v-on:click="toggleEmailDialog"
            v-if="select"
            fab
            small
          >
            <v-icon dark>email</v-icon>
          </v-btn>
          <v-btn
            color="primary"
            raised
            v-on:click="activateSelectArchiveDialog"
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
            v-on:click="unarchiveFab"
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
            {{ $t("actions.add-person") }}
          </v-btn>
        </v-flex>
      </v-layout>
    </v-toolbar>
    <v-data-table
      select-all
      v-model="selected"
      :rows-per-page-items="rowsPerPageItem"
      :headers="headers"
      :items="visibleMembers"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td><v-checkbox v-model="props.selected" primary hide-details /></td>
        <td>{{ props.item.person.firstName }}</td>
        <td>{{ props.item.person.lastName }}</td>
        <td>{{ props.item.person.email }}</td>
        <td>{{ props.item.person.phone }}</td>
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
                v-on:click="confirmArchive(props.item)"
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
                v-on:click="massUnarchive(props.item)"
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
          $t("groups.messages.confirm-member-archive")
        }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelArchive"
            color="secondary"
            flat
            data-cy="cancel-archive"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer />
          <v-btn
            v-on:click="massArchive"
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
              {{ $t("person.actions.add-participant") }}
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
            >{{ $t("events.participants.add") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- New/Edit dialog -->
    <person-dialog
      @snack="showSnackbar"
      @cancel="cancelPerson"
      @refreshPeople="getMembers"
      :dialog-state="dialogState"
      :all-people="people"
      :person="person"
    />

    <!-- Delete dialog -->
    <v-dialog v-model="deleteDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{
          $t("events.participants.confirm-remove")
        }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelDelete"
            color="secondary"
            flat
            data-cy="cancel-delete"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deleteParticipant"
            color="primary"
            raised
            :loading="deleteDialog.loading"
            data-cy="confirm-delete"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Email dialog -->
    <v-dialog v-model="emailDialog.show" max-width="700px">
      <v-card>
        <v-card-title primary-title>
          <div>
            <h3 class="headline mb-0">
              {{ $t("groups.members.email.compose") }}
            </h3>
          </div>
        </v-card-title>
        <v-card-text>
          <v-select
            v-model="email.recipients"
            :label="$t('groups.members.email.to')"
            :items="parsedMembers"
            multiple
            chips
            deletable-chips
            hide-selected
            :no-data-text="$t('groups.messages.no-remaining-members')"
          >
          </v-select>
        </v-card-text>
        <v-card-text>
          <v-select
            v-model="email.cc"
            :label="$t('groups.members.email.cc')"
            :items="parsedMembers"
            multiple
            chips
            deletable-chips
            hide-selected
            :no-data-text="$t('groups.messages.no-remaining-members')"
          >
          </v-select>
        </v-card-text>
        <v-card-text>
          <v-select
            v-model="email.bcc"
            :label="$t('groups.members.email.bcc')"
            :items="parsedMembers"
            multiple
            chips
            deletable-chips
            :no-data-text="$t('groups.messages.no-remaining-members')"
          >
          </v-select>
        </v-card-text>
        <v-card-text>
          <v-text-field
            :label="$t('groups.members.email.subject')"
            v-model="email.subject"
          >
          </v-text-field>
        </v-card-text>
        <v-card-text>
          <v-textarea
            :label="$t('groups.members.email.body')"
            v-model="email.body"
          >
          </v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="toggleEmailDialog"
            color="secondary"
            flat
            data-cy=""
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="sendEmail"
            :disabled="email.recipients.length == 0"
            color="primary"
            raised
            :loading="sendEmail.loading"
            data-cy="confirm-email"
            >{{ $t("groups.members.email.send") }}</v-btn
          >
        </v-card-actions>
      </v-card>
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
import EntitySearch from "../../EntitySearch";
import PersonDialog from "../../PersonDialog";
import {mapState} from "vuex";
export default {
  components: { EntitySearch, PersonDialog },
  name: "GroupMembers",
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
      members: [],
      people: [],
      person: {},
      parsedMembers: [],
      selected: [],
      select: false,
      archiveSelect: false,
      unarchiveSelect: false,
      email: {
        subject: "",
        body: "",
        recipients: [],
        cc: [],
        bcc: [],
        managerName: "",
        managerEmail: ""
      },
      emailDialog: {
        show: false,
        loading: false
      },
      addParticipantDialog: {
        show: false,
        newParticipants: [],
        loading: false
      },
      personDialog: {
        show: false,
        title: "",
        person: {},
        addAnotherEnabled: false,
        saveButtonText: "actions.save"
      },
      deleteDialog: {
        show: false,
        participantId: -1,
        loading: false
      },
      archiveDialog: {
        show: false,
        memberId: -1,
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

      this.email.recipients = this.getEmailRecipients();
    }
  },

  computed: {
    viewOptions() {
      return [
        { text: this.$t("actions.view-active"), value: "viewActive" },
        { text: this.$t("actions.view-archived"), value: "viewArchived" },
        { text: this.$t("actions.view-all"), value: "viewAll" }
      ];
    },

    headers() {
      return [
        {
          text: this.$t("person.name.first"),
          value: "person.firstName",
          width: "20%"
        },
        {
          text: this.$t("person.name.last"),
          value: "person.lastName",
          width: "20%"
        },
        {
          text: this.$t("person.email"),
          value: "person.email",
          width: "22.5%"
        },
        {
          text: this.$t("person.phone"),
          value: "person.phone",
          width: "22.5%"
        },
        {
          text: this.$t("actions.header"),
          sortable: false
        }
      ];
    },

    visibleMembers() {
      let list = this.members;
      if (this.viewStatus === "viewActive") {
        return list.filter(ev => ev.active);
      } else if (this.viewStatus === "viewArchived") {
        return list.filter(ev => !ev.active);
      } else {
        return list;
      }
    },
    ...mapState(['currentAccount'])
  },

  methods: {
    parseMembers() {
      this.members.map(e => {
        if (e.person.email) {
          this.parsedMembers.push({
            text: e.person.firstName + " " + e.person.lastName,
            value: e.person.email
          });
        }
      });
    },

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
      this.person = person;
    },

    cancelPerson() {
      this.dialogState = "";
    },

    addParticipants() {
      this.addParticipantDialog.loading = true;
      let promises = [];
      for (let person of this.addParticipantDialog.newParticipants) {
        const idx = this.members.findIndex(
          gr_pe => gr_pe.person.person_id === person.id
        );
        if (idx === -1) {
          promises.push(this.addParticipant(person.id));
        }
      }

      Promise.all(promises)
        .then(() => {
          this.showSnackbar(this.$t("groups.messages.members-added"));
          this.addParticipantDialog.loading = false;
          this.addParticipantDialog.show = false;
          this.addParticipantDialog.newParticipants = [];
          this.getMembers();
        })
        .catch(err => {
          console.log(err);
          this.addParticipantDialog.loading = false;
          this.showSnackbar(this.$t("groups.messages.error-adding-members"));
        });
    },

    getEmailRecipients() {
      return this.selected
        .map(e => e.person.email)
        .filter(function(e) {
          return e != null;
        });
    },

    sendEmail() {
      this.email['managerEmail'] = this.currentAccount.email;
      this.$http
        .post(`/api/v1/emails/`, this.email)
        .then(() => {
          this.toggleEmailDialog();
          this.selected = [];
          this.email.subject = "";
          this.email.body = "";
          this.email.cc = "";
          this.email.bcc = "";
          this.showSnackbar(this.$t("groups.messages.email-sent"));
        })
        .catch(err => {
          this.showSnackbar(this.$t("groups.messages.error-no-manager-email"));
          console.log(err);
        });
    },

    toggleEmailDialog() {
      if (this.selected.length > 0) {
        this.email.recipients = this.getEmailRecipients();
        this.emailDialog.show = !this.emailDialog.show;
      } else this.showSnackbar("No valid email addresses are selected");
    },

    addParticipant(id) {
      const groupId = this.$route.params.group;
      for (var member of this.members) {
        if (id == member.person.id) {
          return true;
        }
      }
      return this.$http.post(`/api/v1/groups/groups/${groupId}/members`, {
        personId: id,
        joined: "2018-12-25"
      });
    },

    confirmDelete(event) {
      this.activateDeleteDialog(event.person_id);
    },

    deleteParticipant() {
      this.deleteDialog.loading = true;
      const participantId = this.deleteDialog.participantId;
      const idx = this.people.findIndex(ev => ev.person.id === participantId);
      const id = this.$route.params.event;
      this.$http
        .delete(`/api/v1/events/${id}/participants/${participantId}`)
        .then(() => {
          this.deleteDialog.loading = false;
          this.deleteDialog.show = false;
          this.people.splice(idx, 1);
          this.showSnackbar(this.$t("events.participants.removed"));
        })
        .catch(err => {
          console.log(err);
          this.deleteDialog.loading = false;
          this.deleteDialog.show = false;
          this.showSnackbar(this.$t("events.participants.error-removing"));
        });
    },
    cancelDelete() {
      this.deleteDialog.show = false;
    },

    activateDeleteDialog(participantId) {
      this.deleteDialog.show = true;
      this.deleteDialog.participantId = participantId;
    },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },

    containsActive() {
      let isActive = false;
      this.selected.map(e => {
        if (e.active) isActive = true;
      });
      return isActive;
    },

    massArchive() {
      if (this.archiveSelect) {
        this.selected.map(e => {
          this.archiveDialog.memberId = e.id;
          this.archiveGroup();
        });
        this.archiveSelect = false;
      } else this.archiveGroup();
    },

    activateSelectArchiveDialog() {
      if (this.containsActive()) {
        if (this.selected.length == 1) {
          this.activateArchiveDialog(this.selected[0].person.id);
        } else this.archiveDialog.show = true;
        this.archiveSelect = true;
      } else
        this.showSnackbar(this.$t("groups.messages.error-active-not-selected"));
    },

    activateArchiveDialog(memberId) {
      this.archiveDialog.show = true;
      this.archiveDialog.memberId = memberId;
    },

    confirmArchive(event) {
      this.activateArchiveDialog(event.id);
    },

    cancelArchive() {
      this.archiveDialog.show = false;
      this.archiveSelect = false;
    },

    archiveGroup() {
      console.log("Archived member");
      this.archiveDialog.loading = true;
      const memberId = this.archiveDialog.memberId;
      const idx = this.members.findIndex(ev => ev.id === memberId);
      this.$http
        .put(`/api/v1/groups/members/deactivate/${memberId}`)
        .then(resp => {
          console.log("ARCHIVE", resp);
          this.members[idx].active = false;
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          this.showSnackbar(this.$t("groups.messages.member-archived"));
        })
        .catch(err => {
          console.error("ARCHIVE FALURE", err.response);
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          this.showSnackbar(this.$t("groups.messages.error-archiving-member"));
        });
    },

    unarchiveFab() {
      if (!this.containsActive()) {
        this.unarchiveSelect = true;
        this.massUnarchive();
      } else
        this.showSnackbar(
          this.$t("groups.messages.error-archived-not-selected")
        );
    },

    massUnarchive(member) {
      if (this.unarchiveSelect) {
        this.selected.map(e => {
          this.unarchive(e);
        });
        this.unarchiveSelect = false;
      } else this.unarchive(member);
    },

    unarchive(member) {
      const idx = this.members.findIndex(ev => ev.id === member.id);
      const memberId = member.id;
      member.id *= -1; // to show loading spinner
      this.$http
        .put(`/api/v1/groups/members/activate/${memberId}`)
        .then(resp => {
          console.log("UNARCHIVED", resp);
          Object.assign(this.members[idx], resp.data);
          this.showSnackbar(this.$t("groups.messages.member-unarchived"));
        })
        .catch(err => {
          console.error("UNARCHIVE FALURE", err.response);
          this.showSnackbar(
            this.$t("groups.messages.error-unarchiving-member")
          );
        });
    },

    getMembers() {
      this.tableLoading = true;
      const id = this.$route.params.group;
      this.$http.get(`/api/v1/groups/groups/${id}`).then(resp => {
        // will break under the new groups model
        // this.email.managerName =
        //   resp.data.managerInfo.person.firstName +
        //   " " +
        //   resp.data.managerInfo.person.lastName +
        //   " " +
        //   resp.data.managerInfo.person.secondLastName;
        // this.email.managerEmail = resp.data.managerInfo.person.email;
        this.members = resp.data.members;
        this.people = this.members.map(e => e.person);
        this.parseMembers();
        this.tableLoading = false;
      });
    }
  },

  mounted: function() {
    this.getMembers();
  }
};
</script>

<style>
.v-icon {
  display: inline-flex !important;
}
</style>
