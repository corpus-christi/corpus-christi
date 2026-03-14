<template>
  <div>
    <v-btn variant="outlined" color="primary" :to="{ path: '/teams/all' }"
      ><v-icon>arrow_back</v-icon>{{ t("teams.all-teams") }}</v-btn
    >
    <v-row class="vertical-spacer">
      <v-col xs="12" sm="12">
        <v-card>
          <template v-if="pageLoaded">
            <v-container fill-height fluid>
              <v-col xs="9" sm="9" class="align-end">
                <span class="headline">{{ team.description }}</span>
              </v-col>
              <v-row xs="3" sm="3" align="end" justify="end">
                <v-btn variant="text" color="primary" v-on:click="editTeam(team)">
                  <v-icon>edit</v-icon>&nbsp;{{ t("actions.edit") }}
                </v-btn>
              </v-row>
            </v-container>
          </template>
          <v-row v-else justify="center" style="height: 500px;">
            <div class="ma-5 pa-5">
              <v-progress-circular
                indeterminate
                color="primary"
              ></v-progress-circular>
            </div>
          </v-row>
        </v-card>
      </v-col>
    </v-row>

    <v-toolbar>
      <v-toolbar-title>{{ t("teams.members.title") }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="search"
        v-bind:label="t('actions.search')"
        single-line
        hide-details
      ></v-text-field>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        variant="elevated"
        v-on:click="activateNewParticipantDialog"
        data-cy="add-team-member"
      >
        <v-icon dark left>add</v-icon>
        {{ t("teams.members.add") }}
      </v-btn>
    </v-toolbar>
    <v-data-table
      :items-per-page-options="rowsPerPageItem"
      :headers="headers"
      :items="members"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template #item="{ item }">
        <tr>
          <td>{{ item.member.firstName }}</td>
          <td>{{ item.member.lastName }}</td>
          <td>{{ item.member.email }}</td>
          <td>{{ item.member.phone }}</td>
          <td>
            <template v-if="item.active">
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

    <!-- Snackbar -->
    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false">
          {{ t("actions.close") }}
        </v-btn>
      </template>
    </v-snackbar>

    <!-- Archive dialog -->
    <v-dialog v-model="archiveDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{ t("team.members.confirm-remove") }}</v-card-text>
        <v-card-actions>
          <v-btn v-on:click="cancelArchive" color="secondary" variant="text" data-cy="">{{
            t("actions.cancel")
          }}</v-btn>
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="archiveMember"
            color="primary"
            variant="elevated"
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- New/Edit dialog -->
    <v-dialog v-model="teamDialog.show" max-width="500px">
      <TeamForm
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
        <v-card-title>
          <div>
            <h3 class="headline mb-0">{{ t("teams.members.add") }}</h3>
          </div>
        </v-card-title>
        <v-card-text>
          <EntitySearch
            multiple
            person
            v-model="addMemberDialog.newMembers"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelNewParticipantDialog"
            color="secondary"
            variant="text"
            data-cy="cancel-participant"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="addParticipants"
            :disabled="addMemberDialog.newMembers.length == 0"
            color="primary"
            variant="elevated"
            :loading="addMemberDialog.loading"
            data-cy="confirm-participant"
            >{{ t("teams.members.add") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import TeamForm from "./TeamForm.vue";
import EntitySearch from "../EntitySearch.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const route = useRoute();

const rowsPerPageItem = [10, 15, 25, { title: "All", value: -1 }];
const pageLoaded = ref(false);
const tableLoading = ref(false);
const search = ref("");
const team = ref<any>({});
const members = ref<any[]>([]);

const teamDialog = ref({
  show: false,
  editMode: false,
  saveLoading: false,
  addMoreLoading: false,
  team: {} as any
});

const archiveDialog = ref({ show: false, memberId: -1, loading: false });
const addMemberDialog = ref({ show: false, newMembers: [] as any[], loading: false });
const snackbar = ref({ show: false, text: "" });

const headers = computed(() => [
  { title: t("person.name.first"), value: "firstName", width: "20%" },
  { title: t("person.name.last"), value: "lastName", width: "20%" },
  { title: t("person.email"), value: "email", width: "22.5%" },
  { title: t("person.phone"), value: "phone", width: "22.5%" },
  { title: t("actions.header"), sortable: false }
]);

function reloadTeam() {
  const id = route.params.team;
  http.get(`/api/v1/teams/${id}?include_members=1`).then(resp => {
    team.value = resp.data;
    members.value = resp.data.members;
    for (let m of members.value) console.log(m);
    pageLoaded.value = true;
  });
}

function activateArchiveDialog(memberId: number) {
  archiveDialog.value.show = true;
  archiveDialog.value.memberId = memberId;
}

function confirmArchive(member: any) {
  activateArchiveDialog(member.member_id);
}

function cancelArchive() {
  archiveDialog.value.show = false;
}

function archiveMember() {
  archiveDialog.value.loading = true;
  const memberId = archiveDialog.value.memberId;
  const teamId = route.params.team;
  const idx = members.value.findIndex((as: any) => as.member_id === memberId);
  http
    .delete(`/api/v1/teams/${teamId}/members/${memberId}`)
    .then(resp => {
      console.log("ARCHIVE", resp);
      members.value[idx].active = false;
      archiveDialog.value.loading = false;
      archiveDialog.value.show = false;
      showSnackbar(t("assets.asset-archived"));
    })
    .catch(err => {
      console.error("ARCHIVE FALURE", err.response);
      archiveDialog.value.loading = false;
      archiveDialog.value.show = false;
      showSnackbar(t("assets.error-archiving-asset"));
    });
}

function unarchive(member: any) {
  const idx = members.value.findIndex(
    (as: any) => as.member_id === member.member_id
  );
  const copyMember = JSON.parse(JSON.stringify(member));
  member.unarchiving = true;
  copyMember.active = true;
  const patchId = copyMember.member_id;
  const teamId = route.params.team;
  http
    .patch(`/api/v1/teams/${teamId}/members/${patchId}`, { active: true })
    .then(resp => {
      console.log("UNARCHIVED", resp);
      delete member.unarchiving;
      Object.assign(members.value[idx], resp.data);
      showSnackbar(t("assets.asset-unarchived"));
    })
    .catch(err => {
      delete member.unarchiving;
      console.error("UNARCHIVE FALURE", err.response);
      showSnackbar(t("assets.error-unarchiving-asset"));
    });
}

function activateNewParticipantDialog() {
  addMemberDialog.value.newMembers = [];
  addMemberDialog.value.show = true;
}

function cancelNewParticipantDialog() {
  addMemberDialog.value.show = false;
}

function addParticipants() {
  addMemberDialog.value.loading = true;
  let promises: Promise<any>[] = [];

  for (let person of addMemberDialog.value.newMembers) {
    const idx = members.value.findIndex(
      (ev_pe: any) => ev_pe.member_id === person.id
    );
    if (idx === -1) {
      promises.push(addParticipant(person.id));
    }
  }

  Promise.all(promises)
    .then(() => {
      showSnackbar(t("events.participants.added"));
      addMemberDialog.value.loading = false;
      addMemberDialog.value.show = false;
      addMemberDialog.value.newMembers = [];
      reloadTeam();
    })
    .catch(err => {
      console.log(err);
      addMemberDialog.value.loading = false;
      showSnackbar(t("events.participants.error-adding"));
    });
}

function addParticipant(id: number) {
  const teamId = route.params.team;
  return http.post(`/api/v1/teams/${teamId}/members/${id}`, { active: true });
}

function activateTeamDialog(t2: any = {}, editMode = false) {
  teamDialog.value.editMode = editMode;
  teamDialog.value.team = t2;
  teamDialog.value.show = true;
}

function editTeam(t2: any) {
  activateTeamDialog({ ...t2 }, true);
}

function cancelTeam() {
  teamDialog.value.show = false;
}

function saveTeam(t2: any) {
  teamDialog.value.saveLoading = true;
  const teamId = t2.id;
  delete t2.id;
  http
    .patch(`/api/v1/events/teams/${teamId}`, {
      description: t2.description
    })
    .then(resp => {
      console.log("EDITED", resp);
      team.value = resp.data;
      teamDialog.value.show = false;
      teamDialog.value.saveLoading = false;
      showSnackbar(t("teams.team-edited"));
    })
    .catch(err => {
      console.error("PUT FALURE", err.response);
      console.log(err);
      teamDialog.value.saveLoading = false;
      showSnackbar(t("teams.error-editing-team"));
    });
}

function showSnackbar(message: string) {
  snackbar.value.text = message;
  snackbar.value.show = true;
}

onMounted(() => {
  pageLoaded.value = false;
  reloadTeam();
});
</script>

<style scoped>
.vertical-spacer {
  margin-bottom: 20px;
}
</style>
