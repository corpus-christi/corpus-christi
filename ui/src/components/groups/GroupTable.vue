<template>
  <div>
    <v-toolbar class="pa-1">
      <v-row align="center" justify="space-between">
        <v-col md="2">
          <v-toolbar-title>{{ t("groups.header") }}</v-toolbar-title>
        </v-col>
        <v-col md="2">
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="t('actions.search')"
            single-line
            hide-details
            data-cy="form-search"
          />
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
            v-on:click.stop="newGroup"
            data-cy="add-group"
          >
            <v-icon dark left>add</v-icon>
            {{ t("actions.add-group") }}
          </v-btn>
        </v-col>
      </v-row>
    </v-toolbar>

    <v-data-table
      :headers="headers"
      :items-per-page-options="rowsPerPageItem"
      :items="visibleGroups"
      :search="search"
      :loading="tableLoading"
      must-sort
      class="elevation-1"
    >
      <template #item="{ item }">
        <tr>
          <td
            class="hover-hand"
            v-on:click="router.push({ path: '/groups/' + item.id })"
          >
            {{ item.name }}
          </td>
          <td
            class="hover-hand"
            v-on:click="router.push({ path: '/groups/' + item.id })"
          >
            {{ item.description }}
          </td>
          <td
            class="hover-hand"
            v-on:click="router.push({ path: '/groups/' + item.id })"
          >
            {{ getManagerName(item.managerInfo) }}
          </td>
          <td
            class="hover-hand"
            v-on:click="router.push({ path: '/groups/' + item.id })"
          >
            {{ item.memberList.filter((ev: any) => ev.active).length }}
          </td>
          <td class="text-no-wrap">
            <template v-if="item.active">
              <v-tooltip bottom>
                <template #activator="{ props: tooltipProps }">
                  <v-btn
                    icon
                    variant="outlined"
                    size="small"
                    color="primary"
                    v-bind="tooltipProps"
                    v-on:click="editGroup(item)"
                    data-cy="edit"
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
                    :loading="item.id < 0"
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

    <!-- New/Edit dialog -->
    <v-dialog v-model="groupDialog.show" max-width="500px" persistent>
      <GroupForm
        v-bind:editMode="groupDialog.editMode"
        v-bind:initialData="groupDialog.group"
        v-bind:saveLoading="groupDialog.saveLoading"
        v-bind:addMoreLoading="groupDialog.addMoreLoading"
        v-on:cancel="cancelGroup"
        v-on:save="saveGroup"
        v-on:add-another="addAnotherGroup"
      />
    </v-dialog>

    <!-- Archive dialog -->
    <v-dialog v-model="archiveDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{ t("groups.messages.confirm-archive") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelArchive"
            color="secondary"
            variant="text"
            data-cy="cancel-archive"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer />
          <v-btn
            v-on:click="archiveGroup"
            color="primary"
            variant="elevated"
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
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
import { useRouter } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import GroupForm from "./GroupForm.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const router = useRouter();

const rowsPerPageItem = [10, 15, 25, { title: "All", value: -1 }];
const tableLoading = ref(true);
const groups = ref<any[]>([]);
const search = ref("");
const viewStatus = ref("viewActive");

const groupDialog = ref({
  show: false,
  editMode: false,
  saveLoading: false,
  addMoreLoading: false,
  group: {} as any
});

const archiveDialog = ref({
  show: false,
  groupId: -1,
  loading: false
});

const snackbar = ref({ show: false, text: "" });

const viewOptions = computed(() => [
  { title: t("actions.view-active"), value: "viewActive" },
  { title: t("actions.view-archived"), value: "viewArchived" },
  { title: t("actions.view-all"), value: "viewAll" }
]);

const visibleGroups = computed(() => {
  let list = groups.value;
  if (viewStatus.value === "viewActive") {
    return list.filter((ev: any) => ev.active);
  } else if (viewStatus.value === "viewArchived") {
    return list.filter((ev: any) => !ev.active);
  } else {
    return list;
  }
});

const headers = computed(() => [
  { title: t("groups.name"), value: "name" },
  { title: t("groups.description"), value: "description" },
  { title: t("groups.manager"), value: "managerInfo.person.lastName" },
  { title: t("groups.member-count"), value: "memberList.length" },
  { title: t("actions.header"), sortable: false }
]);

function getManagerName(managerInfo: any) {
  var man = managerInfo.person;
  return (
    man.firstName +
    " " +
    man.lastName +
    " " +
    (man.secondLastName ? man.secondLastName : "")
  );
}

function activateGroupDialog(group: any = {}, editMode = false) {
  groupDialog.value.editMode = editMode;
  groupDialog.value.group = group;
  groupDialog.value.show = true;
}

function newGroup() {
  activateGroupDialog();
}

function cancelGroup() {
  groupDialog.value.show = false;
}

function saveGroup(group: any, closeDialog = true) {
  groupDialog.value.saveLoading = true;
  let newGroup = JSON.parse(JSON.stringify(group));
  delete newGroup.manager;
  delete newGroup.id;
  delete newGroup.memberList;
  delete newGroup.managerInfo;
  if (groupDialog.value.editMode) {
    putGroup(group, newGroup);
  } else {
    postGroup(newGroup);
  }
  if (closeDialog) {
    closeDialogFn();
  }
}

function putGroup(group: any, newGroup: any) {
  const groupId = group.id;
  const idx = groups.value.findIndex((ev: any) => ev.id === group.id);
  http
    .patch(`/api/v1/groups/groups/${groupId}`, newGroup)
    .then(resp => {
      Object.assign(groups.value[idx], resp.data);
      groupDialog.value.saveLoading = false;
      showSnackbar(t("groups.messages.group-edited"));
    })
    .catch(err => {
      console.error("PUT FALURE", err.response);
      groupDialog.value.saveLoading = false;
      showSnackbar(t("groups.messages.error-editing-group"));
    });
}

function postGroup(newGroup: any) {
  http
    .post("/api/v1/groups/groups", newGroup)
    .then(resp => {
      groups.value.push(resp.data);
      groupDialog.value.saveLoading = false;
      showSnackbar(t("groups.messages.group-added"));
    })
    .catch(err => {
      console.error("POST FAILURE", err.response);
      groupDialog.value.saveLoading = false;
      showSnackbar(t("groups.messages.error-adding-group"));
    });
}

function closeDialogFn() {
  groupDialog.value.show = false;
}

function editGroup(group: any) {
  activateGroupDialog({ ...group }, true);
}

function activateArchiveDialog(groupId: number) {
  archiveDialog.value.show = true;
  archiveDialog.value.groupId = groupId;
}

function confirmArchive(event: any) {
  activateArchiveDialog(event.id);
}

function cancelArchive() {
  archiveDialog.value.show = false;
}

function archiveGroup() {
  console.log("Archived group");
  archiveDialog.value.loading = true;
  const groupId = archiveDialog.value.groupId;
  const idx = groups.value.findIndex((ev: any) => ev.id === groupId);
  http
    .put(`/api/v1/groups/groups/deactivate/${groupId}`)
    .then(resp => {
      console.log("ARCHIVE", resp);
      groups.value[idx].active = false;
      archiveDialog.value.loading = false;
      archiveDialog.value.show = false;
      showSnackbar(t("groups.messages.group-archived"));
    })
    .catch(err => {
      console.error("ARCHIVE FALURE", err.response);
      archiveDialog.value.loading = false;
      archiveDialog.value.show = false;
      showSnackbar(t("groups.messages.error-archiving-group"));
    });
}

function unarchive(group: any) {
  const idx = groups.value.findIndex((ev: any) => ev.id === group.id);
  const groupId = group.id;
  group.id *= -1;
  http
    .put(`/api/v1/groups/groups/activate/${groupId}`)
    .then(resp => {
      console.log("UNARCHIVED", resp);
      Object.assign(groups.value[idx], resp.data);
      showSnackbar(t("groups.messages.group-unarchived"));
    })
    .catch(err => {
      console.error("UNARCHIVE FALURE", err.response);
      showSnackbar(t("groups.messages.error-unarchiving-gropu"));
    });
}

function duplicate(group: any) {
  const copyGroup = JSON.parse(JSON.stringify(group));
  delete copyGroup.id;
  activateGroupDialog(copyGroup);
}

function addAnotherGroup(group: any) {
  saveGroup(group, false);
}

function showSnackbar(message: string) {
  snackbar.value.text = message;
  snackbar.value.show = true;
}

onMounted(() => {
  tableLoading.value = true;
  http.get("/api/v1/groups/groups").then(resp => {
    groups.value = resp.data;
    tableLoading.value = false;
  });
});
</script>

<style scoped>
.hover-hand {
  cursor: pointer;
}
</style>
