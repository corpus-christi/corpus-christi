<template>
  <div>
    <v-card class="ma-1">
      <template v-if="loaded">
        <v-container fill-height fluid>
          <v-col cols="9" sm="9" class="align-end">
            <span class="headline">{{ t("teams.title") }}</span>
          </v-col>
          <v-row cols="3" sm="3" align="end" justify="end">
            <v-btn
              variant="text"
              color="primary"
              data-cy="add-team-dialog"
              v-on:click="addTeamDialog.show = true"
            >
              <v-icon>add</v-icon>&nbsp;{{ t("teams.new") }}
            </v-btn>
          </v-row>
        </v-container>
        <v-list v-if="teams.length">
          <template v-for="team in teams" :key="'teamDivider' + team.id">
            <v-divider></v-divider>
            <v-list-item>
              <v-container fluid class="pa-0">
                <v-row justify="space-between" align="center">
                  <v-col>{{ team.description }}</v-col>
                  <v-col cols="auto">
                    <v-btn
                      icon
                      variant="outlined"
                      color="primary"
                      :to="{ path: '/teams/' + team.id }"
                      :data-cy="'view-team-' + team.id"
                      ><v-icon>info</v-icon>
                    </v-btn>
                    <v-btn
                      icon
                      variant="outlined"
                      color="primary"
                      v-on:click="showDeleteTeamDialog(team.id)"
                      :data-cy="'deleteTeam-' + team.id"
                      ><v-icon>delete</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>
            </v-list-item>
          </template>
        </v-list>
        <div v-else class="text-center pa-4">
          {{ t("teams.none-assigned") }}
        </div>
      </template>
      <v-row v-else justify="center" style="height: 500px;">
        <div class="ma-5 pa-5">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>
      </v-row>
    </v-card>
    <!-- Add Team dialog -->
    <v-dialog v-model="addTeamDialog.show" persistent max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">{{ t("teams.new") }}</span>
        </v-card-title>
        <v-card-text>
          <EntitySearch
            data-cy="team-entity-search"
            v-model="addTeamDialog.team"
            :existing-entities="teams"
            team
          ></EntitySearch>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="closeAddTeamDialog()"
            color="secondary"
            variant="text"
            :disabled="addTeamDialog.loading"
            data-cy="cancel-add"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="addTeam()"
            color="primary"
            :disabled="!addTeamDialog.team"
            :loading="addTeamDialog.loading"
            data-cy="confirm-add"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- Delete Team dialog -->
    <v-dialog v-model="deleteTeamDialog.show" max-width="350px">
      <v-card>
        <v-card-text>
          <span>{{ t("teams.confirm-remove-from-event") }}</span>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="deleteTeamDialog.show = false"
            color="secondary"
            variant="text"
            :disabled="deleteTeamDialog.loading"
            data-cy="cancel-delete"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deleteTeam()"
            color="primary"
            :loading="deleteTeamDialog.loading"
            data-cy="confirm-delete"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import EntitySearch from "../EntitySearch.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const route = useRoute();

const props = defineProps<{
  teams: any[];
  loaded: boolean;
}>();

const emit = defineEmits(["snackbar", "team-added"]);

const addTeamDialog = ref({ show: false, loading: false, team: null as any });
const deleteTeamDialog = ref({ show: false, loading: false, teamId: -1 });

function closeAddTeamDialog() {
  addTeamDialog.value.loading = false;
  addTeamDialog.value.show = false;
  addTeamDialog.value.team = null;
}

function addTeam() {
  const eventId = route.params.event;
  let teamId = addTeamDialog.value.team.id;
  const idx = props.teams.findIndex(t => t.id === teamId);
  addTeamDialog.value.loading = true;
  if (idx > -1) {
    closeAddTeamDialog();
    emit("snackbar", t("teams.team-on-event"));
    return;
  }

  http
    .post(`/api/v1/events/${eventId}/teams/${teamId}`)
    .then(() => {
      emit("snackbar", t("teams.team-added"));
      closeAddTeamDialog();
      emit("team-added");
    })
    .catch(err => {
      console.log(err);
      addTeamDialog.value.loading = false;
      if (err.response.status == 422) {
        emit("snackbar", t("teams.error-team-assigned"));
      } else {
        emit("snackbar", t("teams.error-adding-team"));
      }
    });
}

function deleteTeam() {
  let id = deleteTeamDialog.value.teamId;
  const idx = props.teams.findIndex(t => t.id === id);
  deleteTeamDialog.value.loading = true;
  const eventId = route.params.event;
  http
    .delete(`/api/v1/events/${eventId}/teams/${id}`)
    .then(resp => {
      console.log("REMOVED", resp);
      deleteTeamDialog.value.show = false;
      deleteTeamDialog.value.loading = false;
      deleteTeamDialog.value.teamId = -1;
      props.teams.splice(idx, 1);
      emit("snackbar", t("teams.team-removed"));
    })
    .catch(err => {
      console.log(err);
      deleteTeamDialog.value.loading = false;
      emit("snackbar", t("teams.error-removing-team"));
    });
}

function showDeleteTeamDialog(teamId: number) {
  deleteTeamDialog.value.teamId = teamId;
  deleteTeamDialog.value.show = true;
}
</script>
