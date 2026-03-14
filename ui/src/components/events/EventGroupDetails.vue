<template>
  <div>
    <v-card class="ma-1">
      <template v-if="loaded">
        <v-container fill-height fluid>
          <v-col cols="9" sm="9" class="align-end">
            <span class="headline">{{ t("groups.title") }}</span>
          </v-col>
          <v-row cols="3" sm="3" align="end" justify="end">
            <v-btn
              variant="text"
              color="primary"
              data-cy="add-group-dialog"
              v-on:click="addGroupDialog.show = true"
            >
              <v-icon>add</v-icon>&nbsp;{{ t("actions.add-group") }}
            </v-btn>
          </v-row>
        </v-container>
        <v-list v-if="groups.length">
          <template v-for="group in groups" :key="'groupDivider' + group.id">
            <v-divider></v-divider>
            <v-list-item>
              <v-container fluid class="pa-0">
                <v-row justify="space-between" align="center">
                  <v-col>{{ group.description }}</v-col>
                  <v-col cols="auto">
                    <v-btn
                      icon
                      variant="outlined"
                      color="primary"
                      :to="{ path: '/groups/' + group.id }"
                      :data-cy="'view-group-' + group.id"
                      ><v-icon>info</v-icon>
                    </v-btn>
                    <v-btn
                      icon
                      variant="outlined"
                      color="primary"
                      v-on:click="showDeleteGroupDialog(group.id)"
                      :data-cy="'deleteGroup-' + group.id"
                      ><v-icon>delete</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>
            </v-list-item>
          </template>
        </v-list>
        <div v-else class="text-center pa-4">
          {{ t("groups.none-assigned") }}
        </div>
      </template>
      <v-row v-else justify="center" style="height: 500px;">
        <div class="ma-5 pa-5">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>
      </v-row>
    </v-card>
    <!-- Add Group dialog -->
    <v-dialog v-model="addGroupDialog.show" persistent max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">{{ t("actions.add-group") }}</span>
        </v-card-title>
        <v-card-text>
          <EntitySearch
            data-cy="group-entity-search"
            v-model="addGroupDialog.group"
            :existing-entities="groups"
            group
          ></EntitySearch>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="closeAddGroupDialog()"
            color="secondary"
            variant="text"
            :disabled="addGroupDialog.loading"
            data-cy="cancel-add"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="addGroup()"
            color="primary"
            :disabled="!addGroupDialog.group"
            :loading="addGroupDialog.loading"
            data-cy="confirm-add"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- Delete Group dialog -->
    <v-dialog v-model="deleteGroupDialog.show" max-width="350px">
      <v-card>
        <v-card-text>
          <span>{{ t("groups.confirm-remove-from-event") }}</span>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="deleteGroupDialog.show = false"
            color="secondary"
            variant="text"
            :disabled="deleteGroupDialog.loading"
            data-cy="cancel-delete"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deleteGroup()"
            color="primary"
            :loading="deleteGroupDialog.loading"
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
  groups: any[];
  loaded: boolean;
}>();

const emit = defineEmits(["snackbar", "group-added"]);

const addGroupDialog = ref({ show: false, loading: false, group: null as any });
const deleteGroupDialog = ref({ show: false, loading: false, groupId: -1 });

function closeAddGroupDialog() {
  addGroupDialog.value.loading = false;
  addGroupDialog.value.show = false;
  addGroupDialog.value.group = null;
}

function addGroup() {
  const eventId = route.params.event;
  let groupId = addGroupDialog.value.group.id;
  const idx = props.groups.findIndex(t => t.id === groupId);
  addGroupDialog.value.loading = true;
  if (idx > -1) {
    closeAddGroupDialog();
    emit("snackbar", t("groups.group-on-event"));
    return;
  }

  http
    .post(`/api/v1/events/${eventId}/groups/${groupId}`)
    .then(() => {
      emit("snackbar", t("groups.group-added"));
      closeAddGroupDialog();
      emit("group-added");
    })
    .catch(err => {
      console.log(err);
      addGroupDialog.value.loading = false;
      if (err.response.status == 422) {
        emit("snackbar", t("groups.error-group-assigned"));
      } else {
        emit("snackbar", t("groups.error-adding-group"));
      }
    });
}

function deleteGroup() {
  let id = deleteGroupDialog.value.groupId;
  const idx = props.groups.findIndex(t => t.id === id);
  deleteGroupDialog.value.loading = true;
  const eventId = route.params.event;
  http
    .delete(`/api/v1/events/${eventId}/groups/${id}`)
    .then(resp => {
      console.log("REMOVED", resp);
      deleteGroupDialog.value.show = false;
      deleteGroupDialog.value.loading = false;
      deleteGroupDialog.value.groupId = -1;
      props.groups.splice(idx, 1);
      emit("snackbar", t("groups.group-removed"));
    })
    .catch(err => {
      console.log(err);
      deleteGroupDialog.value.loading = false;
      emit("snackbar", t("groups.error-removing-group"));
    });
}

function showDeleteGroupDialog(groupId: number) {
  deleteGroupDialog.value.groupId = groupId;
  deleteGroupDialog.value.show = true;
}
</script>
