<template>
  <div>
    <v-card class="ma-1">
      <template v-if="loaded">
        <v-container fill-height fluid>
          <v-col cols="9" sm="9" class="align-end">
            <span class="headline">{{ t("events.persons.title") }}</span>
          </v-col>
          <v-row cols="3" sm="3" align="end" justify="end">
            <v-btn
              variant="text"
              color="primary"
              data-cy="add-person-dialog"
              v-on:click="addPersonDialog.show = true"
            >
              <v-icon>add</v-icon>&nbsp;{{ t("events.persons.new") }}
            </v-btn>
          </v-row>
        </v-container>
        <v-list v-if="persons.length">
          <template v-for="person in persons" :key="'personDivider' + person.id">
            <v-divider></v-divider>
            <v-list-item>
              <v-container fluid class="pa-0">
                <v-row align="center" justify="space-between">
                  <v-col>
                    {{ getFullName(person.person) }}
                    <template v-if="person.description">
                      - {{ person.description }}</template
                    >
                  </v-col>
                  <v-col cols="auto">
                    <v-btn
                      icon
                      variant="outlined"
                      color="primary"
                      v-on:click="openEditDialog(person)"
                      :data-cy="'editPerson-' + person.id"
                      ><v-icon>edit</v-icon>
                    </v-btn>
                    <v-btn
                      icon
                      variant="outlined"
                      color="primary"
                      v-on:click="showDeletePersonDialog(person.id)"
                      :data-cy="'deletePerson-' + person.id"
                      ><v-icon>delete</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>
            </v-list-item>
          </template>
        </v-list>
        <div v-else class="text-center pa-4">
          {{ t("events.persons.none-assigned") }}
        </div>
      </template>
      <v-row v-else justify="center" style="height: 500px;">
        <div class="ma-5 pa-5">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>
      </v-row>
    </v-card>
    <!-- Add Person dialog -->
    <v-dialog v-model="addPersonDialog.show" persistent max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">{{ addPersonDialogTitle }}</span>
        </v-card-title>
        <v-card-text>
          <v-text-field
            readonly
            disabled
            v-if="addPersonDialog.editMode"
            :model-value="getFullName(addPersonDialog.person)"
          ></v-text-field>
          <!-- TODO conditionally hide, don't remove -->
          <div :hidden="addPersonDialog.editMode">
            <EntitySearch
              person
              data-cy="person-entity-search"
              v-model="addPersonDialog.person"
              :existing-entities="persons"
            ></EntitySearch>
          </div>
          <v-textarea
            rows="1"
            v-model="addPersonDialog.description"
            :label="t('events.persons.description')"
            name="description"
            data-cy="description"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="closeAddPersonDialog()"
            color="secondary"
            variant="text"
            :disabled="addPersonDialog.loading"
            data-cy="cancel-add"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="addPerson()"
            color="primary"
            :disabled="!addPersonDialog.person"
            :loading="addPersonDialog.loading"
            data-cy="confirm-add"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- Delete Person dialog -->
    <v-dialog v-model="deletePersonDialog.show" max-width="350px">
      <v-card>
        <v-card-text>
          <span>{{ t("events.persons.confirm-remove-from-event") }}</span>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="deletePersonDialog.show = false"
            color="secondary"
            variant="text"
            :disabled="deletePersonDialog.loading"
            data-cy="cancel-delete"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deletePerson()"
            color="primary"
            :loading="deletePersonDialog.loading"
            data-cy="confirm-delete"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import EntitySearch from "../EntitySearch.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const route = useRoute();

const props = defineProps<{
  persons: any[];
  loaded: boolean;
}>();

const emit = defineEmits(["snackbar", "person-added"]);

const addPersonDialog = ref({
  editMode: false,
  show: false,
  loading: false,
  person: null as any,
  description: ""
});
const deletePersonDialog = ref({ show: false, loading: false, personId: -1 });

const addPersonDialogTitle = computed(() => {
  return addPersonDialog.value.editMode
    ? t("events.persons.edit")
    : t("events.persons.new");
});

function closeAddPersonDialog() {
  addPersonDialog.value.loading = false;
  addPersonDialog.value.show = false;
  addPersonDialog.value.editMode = false;
  addPersonDialog.value.person = null;
  addPersonDialog.value.description = "";
}

function openEditDialog(eventPerson: any) {
  addPersonDialog.value.editMode = true;
  addPersonDialog.value.show = true;
  addPersonDialog.value.person = eventPerson.person;
  addPersonDialog.value.description = eventPerson.description;
}

function addPerson() {
  const eventId = route.params.event;
  let personId = addPersonDialog.value.person.id;
  addPersonDialog.value.loading = true;
  if (!addPersonDialog.value.editMode) {
    const idx = props.persons.findIndex(p => p.id === personId);
    if (idx > -1) {
      closeAddPersonDialog();
      emit("snackbar", t("events.persons.person-on-event"));
      return;
    }
  }
  let body = { description: addPersonDialog.value.description };
  let promise;
  if (addPersonDialog.value.editMode) {
    promise = http.patch(`/api/v1/events/${eventId}/individuals/${personId}`, body);
  } else {
    promise = http.post(`/api/v1/events/${eventId}/individuals/${personId}`, body);
  }
  promise
    .then(() => {
      if (addPersonDialog.value.editMode) {
        emit("snackbar", t("events.persons.person-edited"));
      } else {
        emit("snackbar", t("events.persons.person-added"));
      }
      emit("person-added");
      closeAddPersonDialog();
    })
    .catch(err => {
      console.log(err);
      addPersonDialog.value.loading = false;
      if (err.response.status == 422) {
        emit("snackbar", t("events.persons.error-person-assigned"));
      } else {
        emit("snackbar", t("events.persons.error-adding-person"));
      }
    });
}

function deletePerson() {
  let id = deletePersonDialog.value.personId;
  const idx = props.persons.findIndex(p => p.id === id);
  deletePersonDialog.value.loading = true;
  const eventId = route.params.event;
  http
    .delete(`/api/v1/events/${eventId}/individuals/${id}`)
    .then(resp => {
      console.log("REMOVED", resp);
      deletePersonDialog.value.show = false;
      deletePersonDialog.value.loading = false;
      deletePersonDialog.value.personId = -1;
      props.persons.splice(idx, 1);
      emit("snackbar", t("events.persons.person-removed"));
    })
    .catch(err => {
      console.log(err);
      deletePersonDialog.value.loading = false;
      emit("snackbar", t("events.persons.error-removing-person"));
    });
}

function showDeletePersonDialog(personId: number) {
  deletePersonDialog.value.personId = personId;
  deletePersonDialog.value.show = true;
}

function getFullName(person: any) {
  return `${person.firstName} ${person.lastName}`;
}
</script>
