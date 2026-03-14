<template>
  <div>
    <v-toolbar class="pa-1">
      <v-row align="center" justify="space-between">
        <v-col md="2">
          <v-toolbar-title>{{ t("teams.title") }}</v-toolbar-title>
        </v-col>
        <v-col md="2">
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="t('actions.search')"
            single-line
            hide-details
            data-cy="form-search"
          ></v-text-field>
        </v-col>
        <v-col md="3">
          <v-select
            hide-details
            solo
            single-line
            :items="viewOptions"
            v-model="viewStatus"
            data-cy="view-status-select"
          >
          </v-select>
        </v-col>
        <v-col shrink>
          <v-btn
            color="primary"
            variant="elevated"
            v-on:click.stop="newTeam"
            data-cy="add-team"
          >
            <v-icon dark left>add</v-icon>
            {{ t("teams.new") }}
          </v-btn>
        </v-col>
      </v-row>
    </v-toolbar>

    <v-data-table
      :items-per-page-options="rowsPerPageItem"
      :headers="headers"
      :items="visibleTeams"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template #item="{ item }">
        <tr>
          <td
            class="hover-hand"
            v-on:click="router.push({ path: '/teams/' + item.id })"
          >
            {{ item.description }}
          </td>
          <td>
            <template v-if="item.active">
              <v-tooltip bottom v-if="item.active">
                <template #activator="{ props: tooltipProps }">
                  <v-btn
                    icon
                    variant="outlined"
                    size="small"
                    color="primary"
                    v-bind="tooltipProps"
                    v-on:click="editTeam(item)"
                    data-cy="edit-team"
                  >
                    <v-icon size="small">edit</v-icon>
                  </v-btn>
                </template>
                <span>{{ t("actions.edit") }}</span>
              </v-tooltip>
              <v-tooltip bottom>
                <template #activator="{ props: tooltipProps }">
                  <v-btn
                    icon
                    variant="outlined"
                    size="small"
                    color="primary"
                    v-bind="tooltipProps"
                    v-on:click="duplicate(item)"
                    data-cy="duplicate"
                  >
                    <v-icon size="small">filter_none</v-icon>
                  </v-btn>
                </template>
                <span>{{ t("actions.duplicate") }}</span>
              </v-tooltip>
              <v-tooltip bottom>
                <template #activator="{ props: tooltipProps }">
                  <v-btn
                    icon
                    variant="outlined"
                    size="small"
                    color="primary"
                    v-bind="tooltipProps"
                    v-on:click="confirmArchive(item)"
                    data-cy="archive"
                  >
                    <v-icon size="small">archive</v-icon>
                  </v-btn>
                </template>
                <span>{{ t("actions.tooltips.archive") }}</span>
              </v-tooltip>
            </template>
            <template v-else>
              <v-tooltip bottom v-if="!item.active">
                <template #activator="{ props: tooltipProps }">
                  <v-btn
                    icon
                    variant="outlined"
                    size="small"
                    color="primary"
                    v-bind="tooltipProps"
                    v-on:click="unarchive(item)"
                    :loading="item.unarchiving"
                    data-cy="unarchive"
                  >
                    <v-icon size="small">undo</v-icon>
                  </v-btn>
                </template>
                <span>{{ t("actions.tooltips.activate") }}</span>
              </v-tooltip>
            </template>
          </td>
        </tr>
      </template>
    </v-data-table>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false">
          {{ t("actions.close") }}
        </v-btn>
      </template>
    </v-snackbar>

    <!-- New/Edit dialog -->
    <v-dialog v-model="teamDialog.show" max-width="500px" persistent>
      <TeamForm
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
        <v-card-text>{{ t("teams.confirm-archive") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelArchive"
            color="secondary"
            variant="text"
            data-cy="cancel-archive"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="archiveTeam"
            color="primary"
            variant="elevated"
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import TeamForm from "./TeamForm.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const router = useRouter();

const rowsPerPageItem = [10, 15, 25, { title: "All", value: -1 }];
const tableLoading = ref(true);
const teams = ref<any[]>([]);
const search = ref("");
const addMore = ref(false);
const viewStatus = ref("viewActive");

const teamDialog = ref({
  show: false,
  editMode: false,
  saveLoading: false,
  addMoreLoading: false,
  team: {} as any
});

const archiveDialog = ref({ show: false, teamId: -1, loading: false });
const snackbar = ref({ show: false, text: "" });

const headers = computed(() => [
  { title: t("teams.description"), value: "description", width: "40%" },
  { title: t("actions.header"), sortable: false, width: "20%" }
]);

const viewOptions = computed(() => [
  { title: t("actions.view-active"), value: "viewActive" },
  { title: t("actions.view-archived"), value: "viewArchived" },
  { title: t("actions.view-all"), value: "viewAll" }
]);

const visibleTeams = computed(() => {
  if (viewStatus.value == "viewActive") {
    return teams.value.filter((te: any) => te.active);
  } else if (viewStatus.value == "viewArchived") {
    return teams.value.filter((te: any) => !te.active);
  } else {
    return teams.value;
  }
});

function activateTeamDialog(team: any = {}, editMode = false) {
  teamDialog.value.editMode = editMode;
  teamDialog.value.team = team;
  teamDialog.value.show = true;
}

function editTeam(team: any) {
  activateTeamDialog({ ...team }, true);
}

function activateArchiveDialog(teamId: number) {
  archiveDialog.value.show = true;
  archiveDialog.value.teamId = teamId;
}

function confirmArchive(team: any) {
  activateArchiveDialog(team.id);
}

function duplicate(team: any) {
  const copyTeam = JSON.parse(JSON.stringify(team));
  delete copyTeam.id;
  activateTeamDialog(copyTeam);
}

function archiveTeam() {
  archiveDialog.value.loading = true;
  const teamId = archiveDialog.value.teamId;
  const idx = teams.value.findIndex((te: any) => te.id === teamId);
  http
    .delete(`/api/v1/teams/${teamId}`)
    .then(resp => {
      console.log("ARCHIVE", resp);
      teams.value[idx].active = false;
      archiveDialog.value.loading = false;
      archiveDialog.value.show = false;
      showSnackbar(t("teams.team-archived"));
    })
    .catch(err => {
      console.error("ARCHIVE FALURE", err.response);
      archiveDialog.value.loading = false;
      archiveDialog.value.show = false;
      showSnackbar(t("teams.error-archiving-team"));
    });
}

function unarchive(team: any) {
  const idx = teams.value.findIndex((te: any) => te.id === team.id);
  const copyTeam = JSON.parse(JSON.stringify(team));
  team.unarchiving = true;
  copyTeam.active = true;
  const patchId = copyTeam.id;
  delete copyTeam.id;
  http
    .patch(`/api/v1/teams/${patchId}`, { active: true })
    .then(resp => {
      console.log("UNARCHIVED", resp);
      delete team.unarchiving;
      Object.assign(teams.value[idx], resp.data);
      showSnackbar(t("teams.team-unarchived"));
    })
    .catch(err => {
      delete team.unarchiving;
      console.error("UNARCHIVE FALURE", err.response);
      showSnackbar(t("teams.error-unarchiving-team"));
    });
}

function cancelArchive() {
  archiveDialog.value.show = false;
}

function newTeam() {
  activateTeamDialog();
}

function clearTeam() {
  addMore.value = false;
  teamDialog.value.editMode = false;
  teamDialog.value.saveLoading = false;
  teamDialog.value.addMoreLoading = false;
  teamDialog.value.team = {};
}

function cancelTeam() {
  addMore.value = false;
  teamDialog.value.show = false;
  teamDialog.value.editMode = false;
  teamDialog.value.saveLoading = false;
  teamDialog.value.addMoreLoading = false;
}

function addAnother(team: any) {
  addMore.value = true;
  teamDialog.value.addMoreLoading = true;
  saveTeam(team);
}

function save(team: any) {
  teamDialog.value.saveLoading = true;
  saveTeam(team);
}

function saveTeam(team: any) {
  if (teamDialog.value.editMode) {
    const teamId = team.id;
    const idx = teams.value.findIndex((te: any) => te.id === team.id);
    delete team.id;
    http
      .patch(`/api/v1/teams/${teamId}`, { description: team.description })
      .then(resp => {
        console.log("EDITED", resp);
        Object.assign(teams.value[idx], resp.data);
        cancelTeam();
        showSnackbar(t("teams.team-edited"));
      })
      .catch(err => {
        console.error("PUT FALURE", err.response);
        teamDialog.value.saveLoading = false;
        showSnackbar(t("teams.error-editing-team"));
      });
  } else {
    let newTeam = JSON.parse(JSON.stringify(team));
    delete newTeam.id;
    delete newTeam.active;
    delete newTeam.members;
    http
      .post("/api/v1/teams/", newTeam)
      .then(resp => {
        console.log("ADDED", resp);
        teams.value.push(resp.data);
        if (addMore.value) clearTeam();
        else cancelTeam();
        showSnackbar(t("teams.team-added"));
      })
      .catch(err => {
        console.error("POST FAILURE", err.response);
        teamDialog.value.saveLoading = false;
        teamDialog.value.addMoreLoading = false;
        showSnackbar(t("teams.error-adding-team"));
      });
  }
}

function showSnackbar(message: string) {
  snackbar.value.text = message;
  snackbar.value.show = true;
}

onMounted(() => {
  tableLoading.value = true;
  http.get(`/api/v1/teams/?return_group=all`).then(resp => {
    teams.value = resp.data;
    console.log(resp.data);
    tableLoading.value = false;
  });
});
</script>

<style scoped>
.hover-hand {
  cursor: pointer;
}
</style>
