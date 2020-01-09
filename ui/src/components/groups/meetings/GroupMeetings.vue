<template>
  <div>
    <v-toolbar>
      <v-toolbar-title>{{ $t("groups.meetings.title") }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="search"
        v-bind:label="$t('actions.search')"
        single-line
        hide-details
      ></v-text-field>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        raised
        v-on:click="openMeetingDialog"
        data-cy="add-meeting"
      >
        <v-icon dark left>add</v-icon>
        {{ $t("groups.actions.add-meeting") }}
      </v-btn>
    </v-toolbar>
    <v-data-table
      :rows-per-page-items="rowsPerPageItem"
      :headers="headers"
      :items="members"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td>{{ props.item.person.firstName }}</td>
        <td>{{ props.item.person.lastName }}</td>
        <td>{{ props.item.person.email }}</td>
        <td>{{ props.item.person.phone }}</td>
        <td>
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
                v-on:click="unarchive(props.item)"
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
        <v-card-text>{{ $t("groups.messages.confirm-member-archive") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelArchive"
            color="secondary"
            flat
            data-cy="cancel-archive"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="archiveGroup"
            color="primary"
            raised
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Add Meeting Dialog -->
    <v-dialog v-model="addMeetingDialog.show" max-width="350px">
      <v-card>
        <v-card-title primary-title>
          <div>
            <h3 class="headline mb-0">
              {{ $t("groups.actions.add-meeting") }}
            </h3>
          </div>
        </v-card-title>
        <v-card-text>
          <entity-search
            multiple
            meeting
            v-model="addMeetingDialog.newMeetings"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelNewMeetingDialog"
            color="secondary"
            flat
            data-cy=""
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="addMeetings"
            :disabled="addMeetingDialog.newMeetings.length == 0"
            color="primary"
            raised
            :loading="addMeetingDialog.loading"
            data-cy="confirm-participant"
            >Add Participants</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

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
export default {
  components: { "entity-search": EntitySearch },
  name: "GroupMeetings",
  data() {
    return {
      rowsPerPageItem: [
        10,
        15,
        25,
        { text: "$vuetify.dataIterator.rowsPerPageAll", value: -1 }
      ],
      tableLoading: false,
      search: "",
      members: [],
      addMeetingDialog: {
        show: false,
        newMeetings: [],
        loading: false
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
      }
    };
  },

  computed: {
    headers() {
      return [
        {
          text: this.$t("person.name.first"),
          value: "firstName",
          width: "20%"
        },
        { text: this.$t("person.name.last"), value: "lastName", width: "20%" },
        { text: this.$t("person.email"), value: "email", width: "22.5%" },
        { text: this.$t("person.phone"), value: "phone", width: "22.5%" },
        { text: this.$t("actions.header"), sortable: false }
      ];
    }
  },

  methods: {
    activateNewMeetingDialog() {
      this.addMeetingDialog.show = true;
    },
    openMeetingDialog() {
      this.activateNewMeetingDialog();
    },
    cancelNewMeetingDialog() {
      this.addMeetingDialog.show = false;
    },

    addMeetings() {
      this.addMeetingDialog.loading = true;
      let promises = [];

      for (let person of this.addMeetingDialog.newMeetings) {
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
          this.addMeetingDialog.loading = false;
          this.addMeetingDialog.show = false;
          this.addMeetingDialog.newMeetings = [];
          this.getMembers();
        })
        .catch(err => {
          console.log(err);
          this.addMeetingDialog.loading = false;
          this.showSnackbar(this.$t("groups.messages.error-adding-members"));
        });
    },

    addParticipant(id) {
      const groupId = this.$route.params.group;
      for (var member of this.members) {
        if (id == member.person.id) {
          return true;
        }
      }
      return this.$http.post(`/api/v1/groups/members`, {
        group_id: groupId,
        person_id: id,
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

    activateArchiveDialog(memberId) {
      this.archiveDialog.show = true;
      this.archiveDialog.memberId = memberId;
    },

    confirmArchive(event) {
      console.log(event);
      this.activateArchiveDialog(event.id);
    },

    cancelArchive() {
      this.archiveDialog.show = false;
    },

    archiveGroup() {
      console.log("Archived member");
      this.archiveDialog.loading = true;
      const memberId = this.archiveDialog.memberId;
      console.log(this.archiveDialog.memberId);
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
        this.members = resp.data.memberList;
        this.tableLoading = false;
      });
    }
  },

  mounted: function() {
    this.getMembers();
  }
};
</script>

