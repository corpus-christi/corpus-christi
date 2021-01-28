<template>
  <div>
    <v-card class="ma-1">
      <template v-if="loaded">
        <v-container fill-height fluid>
          <v-flex xs9 sm9 align-end flexbox>
            <span class="headline">{{ $t("teams.title") }}</span>
          </v-flex>
          <v-layout xs3 sm3 align-end justify-end>
            <v-btn
              text
              color="primary"
              data-cy="add-team-dialog"
              v-on:click="addTeamDialog.show = true"
            >
              <v-icon>add</v-icon>&nbsp;{{ $t("teams.new") }}
            </v-btn>
          </v-layout>
        </v-container>
        <v-list v-if="teams.length">
          <template v-for="team in teams">
            <v-divider v-bind:key="'teamDivider' + team.id"></v-divider>
            <v-list-item v-bind:key="team.id">
              <v-list-item-content class="pr-0">
                <v-container fluid class="pa-0">
                  <v-layout justify-space-between align-center>
                    <v-flex>{{ team.description }}</v-flex>
                    <v-flex shrink>
                      <v-layout>
                        <v-flex xs6>
                          <!-- TODO: popup with members instead of rerouting -->
                          <v-btn
                            icon
                            outlined
                            text
                            color="primary"
                            :to="{ path: '/teams/' + team.id }"
                            :data-cy="'view-team-' + team.id"
                            ><v-icon>info</v-icon>
                          </v-btn>
                        </v-flex>
                        <v-flex xs6>
                          <v-btn
                            icon
                            outlined
                            text
                            color="primary"
                            v-on:click="showDeleteTeamDialog(team.id)"
                            :data-cy="'deleteTeam-' + team.id"
                            ><v-icon>delete</v-icon>
                          </v-btn>
                        </v-flex>
                      </v-layout>
                    </v-flex>
                  </v-layout>
                </v-container>
              </v-list-item-content>
            </v-list-item>
          </template>
        </v-list>
        <div v-else class="text-xs-center pa-4">
          {{ $t("teams.none-assigned") }}
        </div>
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
    <!-- Add Team dialog -->
    <v-dialog v-model="addTeamDialog.show" persistent max-width="500px">
      <v-card>
        <v-card-title primary-title>
          <span class="headline">{{ $t("teams.new") }}</span>
        </v-card-title>
        <v-card-text>
          <entity-search
            data-cy="team-entity-search"
            v-model="addTeamDialog.team"
            :existing-entities="teams"
            team
          ></entity-search>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="closeAddTeamDialog()"
            color="secondary"
            text
            :disabled="addTeamDialog.loading"
            data-cy="cancel-add"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer />
          <v-btn
            v-on:click="addTeam()"
            color="primary"
            raised
            :disabled="!addTeamDialog.team"
            :loading="addTeamDialog.loading"
            data-cy="confirm-add"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- Delete Team dialog -->
    <v-dialog v-model="deleteTeamDialog.show" max-width="350px">
      <v-card>
        <v-card-text>
          <span>{{ $t("teams.confirm-remove-from-event") }}</span>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="deleteTeamDialog.show = false"
            color="secondary"
            text
            :disabled="deleteTeamDialog.loading"
            data-cy="cancel-delete"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer />
          <v-btn
            v-on:click="deleteTeam()"
            color="primary"
            raised
            :loading="deleteTeamDialog.loading"
            data-cy="confirm-delete"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>
<script>
import EntitySearch from "../EntitySearch";

export default {
  name: "EventTeamDetails",
  components: {
    "entity-search": EntitySearch,
  },

  props: {
    teams: {
      required: true,
    },
    loaded: {
      type: Boolean,
      required: true,
    },
  },

  data() {
    return {
      addTeamDialog: {
        show: false,
        loading: false,
        team: null,
      },

      deleteTeamDialog: {
        show: false,
        loading: false,
        teamId: -1,
      },
    };
  },

  methods: {
    closeAddTeamDialog() {
      this.addTeamDialog.loading = false;
      this.addTeamDialog.show = false;
      this.addTeamDialog.team = null;
    },

    addTeam() {
      this.addTeamDialog.loading = true;
      // Emit team-added event
      this.$emit("team-added", { team: this.addTeamDialog.team });
      this.closeAddTeamDialog();
    },

    deleteTeam() {
      let id = this.deleteTeamDialog.teamId;
      this.deleteTeamDialog.loading = true;
      // Emit team-deleted event
      this.$emit("team-deleted", { teamId: id });
      this.deleteTeamDialog.show = false;
      this.deleteTeamDialog.loading = false;
      this.deleteTeamDialog.groupId = -1;
    },

    showDeleteTeamDialog(teamId) {
      this.deleteTeamDialog.teamId = teamId;
      this.deleteTeamDialog.show = true;
    },

    showSnackbar(message) {
      this.$emit("snackbar", message);
    },
  },
};
</script>
