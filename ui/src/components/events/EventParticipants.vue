<template>
  <div>
    <v-toolbar>
      <v-toolbar-title>{{ t("events.participants.title") }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="search"
        :label="t('actions.search')"
        single-line
        hide-details
      ></v-text-field>
      <v-spacer></v-spacer>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        v-on:click="openParticipantDialog"
        data-cy="add-participant"
      >
        <v-icon dark left>add</v-icon>
        {{ t("actions.add-person") }}
      </v-btn>
    </v-toolbar>
    <v-data-table
      :headers="headers"
      :items="people"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template #item="{ item }">
        <tr>
          <td>{{ item.person.firstName }}</td>
          <td>{{ item.person.lastName }}</td>
          <td>{{ item.person.email }}</td>
          <td>{{ item.person.phone }}</td>
          <td>
            <v-tooltip location="bottom">
              <template #activator="{ props: tooltipProps }">
                <v-btn
                  icon
                  variant="outlined"
                  size="small"
                  color="primary"
                  v-bind="tooltipProps"
                  v-on:click="confirmDelete(item)"
                  data-cy="archive"
                >
                  <v-icon size="small">delete</v-icon>
                </v-btn>
              </template>
              <span>{{ t("actions.tooltips.remove") }}</span>
            </v-tooltip>
          </td>
        </tr>
      </template>
    </v-data-table>

    <!-- Add Participant Dialog -->
    <v-dialog v-model="addParticipantDialog.show" max-width="350px">
      <v-card>
        <v-card-title>
          <div>
            <h3 class="headline mb-0">
              {{ t("person.actions.add-participant") }}
            </h3>
          </div>
        </v-card-title>
        <v-card-text>
          <!-- TODO maybe include existingEntities -->
          <EntitySearch
            multiple
            person
            v-model="addParticipantDialog.newParticipants"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelNewParticipantDialog"
            color="secondary"
            variant="text"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="addParticipants"
            :disabled="addParticipantDialog.newParticipants.length == 0"
            color="primary"
            :loading="addParticipantDialog.loading"
            data-cy="confirm-participant"
            >{{ t("events.participants.add") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete dialog -->
    <v-dialog v-model="deleteDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{ t("events.participants.confirm-remove") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelDelete"
            color="secondary"
            variant="text"
            data-cy="cancel-delete"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deleteParticipant"
            color="primary"
            :loading="deleteDialog.loading"
            data-cy="confirm-delete"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false">
          {{ t("actions.close") }}
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import EntitySearch from "../EntitySearch.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const route = useRoute();

const tableLoading = ref(false);
const search = ref("");
const people = ref<any[]>([]);
const addParticipantDialog = ref({ show: false, newParticipants: [] as any[], loading: false });
const deleteDialog = ref({ show: false, participantId: -1, loading: false });
const snackbar = ref({ show: false, text: "" });

const headers = computed(() => [
  { title: t("person.name.first"), value: "person.firstName", width: "20%" },
  { title: t("person.name.last"), value: "person.lastName", width: "20%" },
  { title: t("person.email"), value: "person.email", width: "22.5%" },
  { title: t("person.phone"), value: "person.phone", width: "22.5%" },
  { title: t("actions.header"), sortable: false }
]);

function activateNewParticipantDialog() {
  addParticipantDialog.value.show = true;
}

function openParticipantDialog() {
  activateNewParticipantDialog();
}

function cancelNewParticipantDialog() {
  addParticipantDialog.value.show = false;
}

function addParticipants() {
  addParticipantDialog.value.loading = true;
  let promises = [];

  for (let person of addParticipantDialog.value.newParticipants) {
    const idx = people.value.findIndex(ev_pe => ev_pe.person_id === person.id);
    if (idx === -1) {
      promises.push(addParticipant(person.id));
    }
  }

  Promise.all(promises)
    .then(() => {
      showSnackbar(t("events.participants.added"));
      addParticipantDialog.value.loading = false;
      addParticipantDialog.value.show = false;
      addParticipantDialog.value.newParticipants = [];
      getParticipants();
    })
    .catch(err => {
      console.log(err);
      addParticipantDialog.value.loading = false;
      showSnackbar(t("events.participants.error-adding"));
    });
}

function addParticipant(id: number) {
  const eventId = route.params.event;
  return http.post(`/api/v1/events/${eventId}/participants/${id}`, {
    confirmed: true
  });
}

function confirmDelete(event: any) {
  activateDeleteDialog(event.person_id);
}

function deleteParticipant() {
  deleteDialog.value.loading = true;
  const participantId = deleteDialog.value.participantId;
  const idx = people.value.findIndex(ev => ev.person.id === participantId);
  const id = route.params.event;
  http
    .delete(`/api/v1/events/${id}/participants/${participantId}`)
    .then(() => {
      deleteDialog.value.loading = false;
      deleteDialog.value.show = false;
      people.value.splice(idx, 1);
      showSnackbar(t("events.participants.removed"));
    })
    .catch(err => {
      console.log(err);
      deleteDialog.value.loading = false;
      deleteDialog.value.show = false;
      showSnackbar(t("events.participants.error-removing"));
    });
}

function cancelDelete() {
  deleteDialog.value.show = false;
}

function activateDeleteDialog(participantId: number) {
  deleteDialog.value.show = true;
  deleteDialog.value.participantId = participantId;
}

function showSnackbar(message: string) {
  snackbar.value.text = message;
  snackbar.value.show = true;
}

function getParticipants() {
  tableLoading.value = true;
  const id = route.params.event;
  http
    .get(`/api/v1/events/${id}?include_participants=1`)
    .then(resp => {
      let event = resp.data;
      people.value = event.participants;
      tableLoading.value = false;
    });
}

onMounted(() => {
  getParticipants();
});
</script>
