<template>
  <div>
    <v-btn outline color="primary" :to="{ path: '/teams/all' }"
      ><v-icon>arrow_back</v-icon>{{ $t("teams.all-teams") }}</v-btn
    >
    <v-layout class="vertical-spacer">
      <v-flex xs12 sm12>
        <v-card>
          <template v-if="pageLoaded">
            <v-container fill-height fluid>
              <v-flex xs9 sm9 align-end flexbox>
                <span class="headline">{{ team.description }}</span>
              </v-flex>
              <v-layout xs3 sm3 align-end justify-end>
                <v-btn flat color="primary" v-on:click="editTeam(team)">
                  <v-icon>edit</v-icon>&nbsp;{{ $t("actions.edit") }}
                </v-btn>
              </v-layout>
            </v-container>
          </template>
          <v-layout v-else justify-center height="500px">
            <div class="ma-5 pa-5">
              <v-progress-circular
                indeterminate
                color="primary"
              ></v-progress-circular>
            </div>
          </v-layout>
        </v-card>
      </v-flex>
    </v-layout>

    <v-toolbar>
      <v-toolbar-title>{{ $t("teams.members.title") }}</v-toolbar-title>
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
        v-on:click="activateNewParticipantDialog"
        data-cy="add-team-member"
      >
        <v-icon dark left>add</v-icon>
        {{ $t("teams.members.add") }}
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
        <td>{{ props.item.member.firstName }}</td>
        <td>{{ props.item.member.lastName }}</td>
        <td>{{ props.item.member.email }}</td>
        <td>{{ props.item.member.phone }}</td>
        <td>
          <template v-if="props.item.active">
            <!-- TODO change archive to remove -->
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
                :loading="props.item.unarchiving"
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

    <!-- Snackbar -->
    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false">
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>

    <!-- Archive dialog -->
    <v-dialog v-model="archiveDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{ $t("team.members.confirm-remove") }}</v-card-text>
        <v-card-actions>
          <v-btn v-on:click="cancelArchive" color="secondary" flat data-cy="">{{
            $t("actions.cancel")
          }}</v-btn>
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="archiveMember"
            color="primary"
            raised
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- New/Edit dialog -->
    <!-- TODO: This doesn't need to be in its own file -->
    <v-dialog v-model="teamDialog.show" max-width="500px">
      <team-form
        v-bind:editMode="teamDialog.editMode"
        v-bind:initialData="teamDialog.team"
        v-bind:saveLoading="teamDialog.saveLoading"
        v-bind:addMoreLoading="teamDialog.addMoreLoading"
        v-on:save="saveTeam"
        v-on:cancel="cancelTeam"
      />
    </v-dialog>

    <!-- Add Member Dialog -->
    <v-dialog v-model="addMemberDialog.show" max-width="350px" persistent>
      <v-card>
        <v-card-title primary-title>
          <div>
            <h3 class="headline mb-0">{{ $t("teams.members.add") }}</h3>
          </div>
        </v-card-title>
        <v-card-text>
          <entity-search
            multiple
            person
            exisiting-entities="members.member_id"
            :value-comparator="members.member_id"
            v-model="addMemberDialog.newMembers"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelNewParticipantDialog"
            color="secondary"
            flat
            data-cy="cancel-participant"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="addParticipants"
            :disabled="addMemberDialog.newMembers.length == 0"
            color="primary"
            raised
            :loading="addMemberDialog.loading"
            data-cy="confirm-participant"
            >{{ $t("teams.members.add") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import TeamForm from "./TeamForm";
import EntitySearch from "../EntitySearch";
export default {
  name: "Team",
  components: { "team-form": TeamForm, "entity-search": EntitySearch },
  data() {
    return {
      rowsPerPageItem: [
        10,
        15,
        25,
        { text: "$vuetify.dataIterator.rowsPerPageAll", value: -1 }
      ],
      pageLoaded: false,
      tableLoading: false,
      search: "",
      team: {},
      members: [],

      teamDialog: {
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        team: {}
      },

      archiveDialog: {
        show: false,
        memberId: -1,
        loading: false
      },

      addMemberDialog: {
        show: false,
        newMembers: [],
        loading: false
      },
      snackbar: {
        show: false,
        text: ""
      }
    };
  },

  mounted() {
    this.pageLoaded = false;
    this.reloadTeam();
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
    reloadTeam() {
      const id = this.$route.params.team;
      this.$http.get(`/api/v1/teams/${id}?include_members=1`).then(resp => {
        this.team = resp.data;
        this.members = resp.data.members;
        for (let m of this.members) console.log(m);
        this.pageLoaded = true;
      });
    },

    activateArchiveDialog(memberId) {
      this.archiveDialog.show = true;
      this.archiveDialog.memberId = memberId;
    },

    confirmArchive(member) {
      this.activateArchiveDialog(member.member_id);
    },
    cancelArchive() {
      this.archiveDialog.show = false;
    },

    archiveMember() {
      this.archiveDialog.loading = true;
      const memberId = this.archiveDialog.memberId;
      const teamId = this.$route.params.team;
      const idx = this.members.findIndex(as => as.member_id === memberId);
      this.$http
        .delete(`/api/v1/teams/${teamId}/members/${memberId}`)
        .then(resp => {
          console.log("ARCHIVE", resp);
          this.members[idx].active = false;
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          this.showSnackbar(this.$t("assets.asset-archived"));
        })
        .catch(err => {
          console.error("ARCHIVE FALURE", err.response);
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          this.showSnackbar(this.$t("assets.error-archiving-asset"));
        });
    },

    unarchive(member) {
      const idx = this.members.findIndex(
        as => as.member_id === member.member_id
      );
      const copyMember = JSON.parse(JSON.stringify(member));
      member.unarchiving = true;
      copyMember.active = true;
      const patchId = copyMember.member_id;
      const teamId = this.$route.params.team;
      this.$http
        .patch(`/api/v1/teams/${teamId}/members/${patchId}`, { active: true })
        .then(resp => {
          console.log("UNARCHIVED", resp);
          delete member.unarchiving;
          Object.assign(this.members[idx], resp.data);
          this.showSnackbar(this.$t("assets.asset-unarchived"));
        })
        .catch(err => {
          delete member.unarchiving;
          console.error("UNARCHIVE FALURE", err.response);
          this.showSnackbar(this.$t("assets.error-unarchiving-asset"));
        });
    },

    activateNewParticipantDialog() {
      this.addMemberDialog.newMembers = [];
      this.addMemberDialog.show = true;
    },

    cancelNewParticipantDialog() {
      this.addMemberDialog.show = false;
    },

    addParticipants() {
      this.addMemberDialog.loading = true;
      let promises = [];

      for (let person of this.addMemberDialog.newMembers) {
        const idx = this.members.findIndex(
          ev_pe => ev_pe.member_id === person.id
        );
        if (idx === -1) {
          promises.push(this.addParticipant(person.id));
        }
      }

      Promise.all(promises)
        .then(() => {
          this.showSnackbar(this.$t("events.participants.added"));
          this.addMemberDialog.loading = false;
          this.addMemberDialog.show = false;
          this.addMemberDialog.newMembers = [];
          this.reloadTeam();
        })
        .catch(err => {
          console.log(err);
          this.addMemberDialog.loading = false;
          this.showSnackbar(this.$t("events.participants.error-adding"));
        });
    },

    addParticipant(id) {
      const teamId = this.$route.params.team;
      return this.$http.post(`/api/v1/teams/${teamId}/members/${id}`, {
        active: true
      });
    },

    activateTeamDialog(team = {}, editMode = false) {
      this.teamDialog.editMode = editMode;
      this.teamDialog.team = team;
      this.teamDialog.show = true;
    },

    editTeam(team) {
      this.activateTeamDialog({ ...team }, true);
    },

    cancelTeam() {
      this.teamDialog.show = false;
    },

    saveTeam(team) {
      this.teamDialog.saveLoading = true;
      const teamId = team.id;
      delete team.id;
      this.$http
        .patch(`/api/v1/events/teams/${teamId}`, {
          description: team.description
        })
        .then(resp => {
          console.log("EDITED", resp);
          this.team = resp.data;
          this.teamDialog.show = false;
          this.teamDialog.saveLoading = false;
          this.showSnackbar(this.$t("teams.team-edited"));
        })
        .catch(err => {
          console.error("PUT FALURE", err.response);
          console.log(err);
          this.teamDialog.saveLoading = false;
          this.showSnackbar(this.$t("teams.error-editing-team"));
        });
    },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    }
  }
};
</script>

<style scoped>
.vertical-spacer {
  margin-bottom: 20px;
}
</style>
