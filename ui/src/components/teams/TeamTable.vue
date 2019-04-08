<template>
  <div>
    <v-toolbar class="pa-1">
      <v-layout align-center justify-space-between fill-height>
        <v-flex md2>
          <v-toolbar-title>{{ $t("teams.title") }}</v-toolbar-title>
        </v-flex>
        <v-flex md2>
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="$t('actions.search')"
            single-line
            hide-details
            data-cy="form-search"
          ></v-text-field>
        </v-flex>
        <v-flex md3>
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
            v-on:click.stop="newTeam"
            data-cy="add-team"
          >
            <v-icon dark left>add</v-icon>
            {{ $t("teams.new") }}
          </v-btn>
        </v-flex>
      </v-layout>
    </v-toolbar>

    <v-data-table
      :rows-per-page-items="rowsPerPageItem"
      :headers="headers"
      :items="visibleTeams"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td
          class="hover-hand"
          v-on:click="$router.push({ path: '/teams/' + props.item.id })"
        >
          {{ props.item.description }}
        </td>
        <td>
          <template v-if="props.item.active">
            <v-tooltip bottom v-if="props.item.active">
              <v-btn
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="editTeam(props.item)"
                data-cy="edit-team"
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
                v-on:click="duplicate(props.item)"
                data-cy="duplicate"
              >
                <v-icon small>filter_none</v-icon>
              </v-btn>
              <span>{{ $t("actions.duplicate") }}</span>
            </v-tooltip>
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

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false">
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>

    <!-- New/Edit dialog -->
    <v-dialog v-model="teamDialog.show" max-width="500px" persistent>
      <team-form
        v-bind:editMode="teamDialog.editMode"
        v-bind:initialData="teamDialog.team"
        v-bind:saveLoading="teamDialog.saveLoading"
        v-bind:addMoreLoading="teamDialog.addMoreLoading"
        v-on:addAnother="addAnother"
        v-on:save="save"
        v-on:cancel="cancelTeam"
      />
    </v-dialog>

    <!-- Archive dialog -->
    <v-dialog v-model="archiveDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{ $t("teams.confirm-archive") }}</v-card-text>
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
            v-on:click="archiveTeam"
            color="primary"
            raised
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import TeamForm from "./TeamForm";
import { mapGetters } from "vuex";

export default {
  name: "TeamTable",
  components: { "team-form": TeamForm },
  mounted() {
    this.tableLoading = true;
    this.$http.get(`/api/v1/teams/?return_group=all`).then(resp => {
      this.teams = resp.data;
      console.log(resp.data);
      this.tableLoading = false;
    });
  },

  data() {
    return {
      rowsPerPageItem: [
        10,
        15,
        25,
        { text: "$vuetify.dataIterator.rowsPerPageAll", value: -1 }
      ],
      tableLoading: true,
      teams: [],
      teamDialog: {
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        team: {}
      },

      archiveDialog: {
        show: false,
        teamId: -1,
        loading: false
      },
      search: "",

      snackbar: {
        show: false,
        text: ""
      },
      addMore: false,
      viewStatus: "viewActive",

      windowSize: {
        x: 0,
        y: 0,
        screen
      }
    };
  },
  computed: {
    headers() {
      return [
        {
          text: this.$t("teams.description"),
          value: "description",
          width: "40%"
        },
        { text: this.$t("actions.header"), sortable: false, width: "20%" }
      ];
    },

    viewOptions() {
      return [
        { text: this.$t("actions.view-active"), value: "viewActive" },
        { text: this.$t("actions.view-archived"), value: "viewArchived" },
        { text: this.$t("actions.view-all"), value: "viewAll" }
      ];
    },

    visibleTeams() {
      if (this.viewStatus == "viewActive") {
        return this.teams.filter(te => te.active);
      } else if (this.viewStatus == "viewArchived") {
        return this.teams.filter(te => !te.active);
      } else {
        return this.teams;
      }
    },

    ...mapGetters(["currentLanguageCode"])
  },
  methods: {
    activateTeamDialog(team = {}, editMode = false) {
      this.teamDialog.editMode = editMode;
      this.teamDialog.team = team;
      this.teamDialog.show = true;
    },

    editTeam(team) {
      this.activateTeamDialog({ ...team }, true);
    },

    activateArchiveDialog(teamId) {
      this.archiveDialog.show = true;
      this.archiveDialog.teamId = teamId;
    },

    confirmArchive(team) {
      this.activateArchiveDialog(team.id);
    },

    duplicate(team) {
      const copyTeam = JSON.parse(JSON.stringify(team));
      delete copyTeam.id;
      this.activateTeamDialog(copyTeam);
    },

    archiveTeam() {
      this.archiveDialog.loading = true;
      const teamId = this.archiveDialog.teamId;
      const idx = this.teams.findIndex(te => te.id === teamId);
      this.$http
        .delete(`/api/v1/teams/${teamId}`)
        .then(resp => {
          console.log("ARCHIVE", resp);
          this.teams[idx].active = false;
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          this.showSnackbar(this.$t("teams.team-archived"));
        })
        .catch(err => {
          console.error("ARCHIVE FALURE", err.response);
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          this.showSnackbar(this.$t("teams.error-archiving-team"));
        });
    },

    unarchive(team) {
      const idx = this.teams.findIndex(te => te.id === team.id);
      const copyTeam = JSON.parse(JSON.stringify(team));
      team.unarchiving = true;
      copyTeam.active = true;
      const patchId = copyTeam.id;
      delete copyTeam.id;
      this.$http
        .patch(`/api/v1/teams/${patchId}`, { active: true })
        .then(resp => {
          console.log("UNARCHIVED", resp);
          delete team.unarchiving;
          Object.assign(this.teams[idx], resp.data);
          this.showSnackbar(this.$t("teams.team-unarchived"));
        })
        .catch(err => {
          delete team.unarchiving;
          console.error("UNARCHIVE FALURE", err.response);
          this.showSnackbar(this.$t("teams.error-unarchiving-team"));
        });
    },

    cancelArchive() {
      this.archiveDialog.show = false;
    },

    newTeam() {
      this.activateTeamDialog();
    },

    clearTeam() {
      this.addMore = false;
      this.teamDialog.editMode = false;
      this.teamDialog.saveLoading = false;
      this.teamDialog.addMoreLoading = false;
      this.teamDialog.team = {};
    },

    cancelTeam() {
      this.addMore = false;
      this.teamDialog.show = false;
      this.teamDialog.editMode = false;
      this.teamDialog.saveLoading = false;
      this.teamDialog.addMoreLoading = false;
    },

    addAnother(team) {
      this.addMore = true;
      this.teamDialog.addMoreLoading = true;
      this.saveTeam(team);
    },

    save(team) {
      this.teamDialog.saveLoading = true;
      this.saveTeam(team);
    },

    saveTeam(team) {
      if (this.teamDialog.editMode) {
        const teamId = team.id;
        const idx = this.teams.findIndex(te => te.id === team.id);
        delete team.id;
        this.$http
          .patch(`/api/v1/teams/${teamId}`, {
            description: team.description
          })
          .then(resp => {
            console.log("EDITED", resp);
            Object.assign(this.teams[idx], resp.data);
            this.cancelTeam();
            this.showSnackbar(this.$t("teams.team-edited"));
          })
          .catch(err => {
            console.error("PUT FALURE", err.response);
            this.teamDialog.saveLoading = false;
            this.showSnackbar(this.$t("teams.error-editing-team"));
          });
      } else {
        let newTeam = JSON.parse(JSON.stringify(team));
        delete newTeam.id;
        delete newTeam.active;
        delete newTeam.members;
        // for(var i=0; i<newTeam.members.length; i++) {
        //   newTeam.members[i] = {
        //     active: true,
        //     member: newTeam.members[i]
        //   }
        // }
        this.$http
          .post("/api/v1/teams/", newTeam)
          .then(resp => {
            console.log("ADDED", resp);
            this.teams.push(resp.data);
            if (this.addMore) this.clearTeam();
            else this.cancelTeam();
            this.showSnackbar(this.$t("teams.team-added"));
          })
          .catch(err => {
            console.error("POST FAILURE", err.response);
            this.teamDialog.saveLoading = false;
            this.teamDialog.addMoreLoading = false;
            this.showSnackbar(this.$t("teams.error-adding-team"));
          });
      }
    },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },

    onResize() {
      this.windowSize = { x: window.innerWidth, y: window.innerHeight };
      if (this.windowSize.x <= 960) {
        this.windowSize.small = true;
      } else {
        this.windowSize.small = false;
      }
    }
  }
};
</script>

<style scoped>
.hover-hand {
  cursor: pointer;
}
</style>
