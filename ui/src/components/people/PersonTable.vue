<template>
  <div>
    <!-- Header -->
    <v-toolbar class="pa-1" data-cy="person-toolbar">
      <v-row align="center" justify="space-between">
        <v-col md="2">
          <v-toolbar-title>{{ t("people.title") }}</v-toolbar-title>
        </v-col>
        <v-col md="3">
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="t('actions.search')"
            hide-details
            clearable
            single-line
            data-cy="search"
          />
        </v-col>
        <v-col md="3">
          <div data-cy="view-dropdown">
            <v-select
              hide-details
              solo
              single-line
              :items="viewOptions"
              v-model="viewStatus"
            />
          </div>
        </v-col>
        <v-col shrink>
          <v-btn
            class="mr-0 ml-0"
            color="primary"
            variant="elevated"
            v-on:click.stop="newPerson"
            data-cy="new-person"
          >
            <v-icon left>person_add</v-icon>
            {{ t("actions.add-person") }}
          </v-btn>
        </v-col>
      </v-row>
    </v-toolbar>

    <!-- Table of existing people -->
    <v-data-table
      :headers="headers"
      :items="peopleToDisplay"
      :search="search"
      :loading="!tableLoaded"
      class="elevation-1"
      data-cy="person-table"
    >
      <template #item="{ item }">
        <tr>
          <td :data-cy="'first-name-' + item.id">
            {{ item.firstName }}
          </td>
          <td :data-cy="'last-name-' + item.id">
            {{ item.lastName }}
          </td>
          <td class="hidden-sm-and-down" :data-cy="'email-' + item.id">
            {{ item.email }}
          </td>
          <td :data-cy="'phone-' + item.id">{{ item.phone }}</td>
          <td class="text-no-wrap">
            <v-tooltip bottom>
              <template #activator="{ props: tooltipProps }">
                <v-btn
                  icon
                  variant="outlined"
                  size="small"
                  color="primary"
                  v-bind="tooltipProps"
                  v-on:click="editPerson(item)"
                  data-cy="edit-person"
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
                  v-on:click="adminPerson(item)"
                  data-cy="account-settings"
                >
                  <v-icon size="small">settings</v-icon>
                </v-btn>
              </template>
              <span>{{ t("actions.tooltips.settings") }}</span>
            </v-tooltip>
            <v-tooltip bottom v-if="item.active === true">
              <template #activator="{ props: tooltipProps }">
                <v-btn
                  icon
                  variant="outlined"
                  size="small"
                  color="primary"
                  v-bind="tooltipProps"
                  v-on:click="showConfirmDialog('deactivate', item)"
                  data-cy="deactivate-person"
                >
                  <v-icon size="small">archive</v-icon>
                </v-btn>
              </template>
              <span>{{ t("actions.tooltips.archive") }}</span>
            </v-tooltip>
            <v-tooltip bottom v-if="item.active === false">
              <template #activator="{ props: tooltipProps }">
                <v-btn
                  icon
                  variant="outlined"
                  size="small"
                  color="primary"
                  v-bind="tooltipProps"
                  v-on:click="showConfirmDialog('activate', item)"
                  data-cy="reactivate-person"
                >
                  <v-icon size="small">undo</v-icon>
                </v-btn>
              </template>
              <span>{{ t("actions.tooltips.activate") }}</span>
            </v-tooltip>
          </td>
        </tr>
      </template>
    </v-data-table>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false" data-cy>
          {{ t("actions.close") }}
        </v-btn>
      </template>
    </v-snackbar>

    <!-- New/Edit dialog -->
    <person-dialog
      @snack="showSnackbar"
      @cancel="cancelPerson"
      @refreshPeople="refreshPeopleList"
      :dialog-state="dialogState"
      :all-people="allPeople"
      :person="person"
    />

    <!-- Person admin dialog -->
    <v-dialog
      scrollable
      persistent
      v-model="adminDialog.show"
      max-width="500px"
    >
      <PersonAdminForm
        v-bind:person="adminDialog.person"
        v-bind:account="adminDialog.account"
        v-bind:rolesEnabled="adminDialog.rolesEnabled"
        v-bind:rolesList="rolesList"
        v-on:addAccount="addAccount"
        v-on:updateAccount="updateAccount"
        v-on:deactivateAccount="deactivateAccount"
        v-on:reactivateAccount="reactivateAccount"
        v-on:close="closeAdmin"
      />
    </v-dialog>

    <v-dialog
      v-model="confirmDialog.show"
      max-width="350px"
      data-cy="person-table-confirmation"
    >
      <v-card>
        <v-card-text>{{ t(confirmDialog.title) }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelAction"
            color="secondary"
            variant="text"
            :disabled="confirmDialog.loading"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer />
          <v-btn
            v-on:click="confirmAction(confirmDialog.action, confirmDialog.person)"
            color="primary"
            variant="elevated"
            :disabled="confirmDialog.loading"
            :loading="confirmDialog.loading"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import PersonDialog from "../PersonDialog.vue";
import PersonAdminForm from "./AccountForm.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;

const props = defineProps<{
  peopleList: any[];
  rolesList: any[];
  tableLoaded: boolean;
}>();

const emit = defineEmits(["fetchPeopleList"]);

const viewStatus = ref("viewActive");
const adminDialog = ref({
  show: false,
  person: {} as any,
  account: {} as any,
  rolesEnabled: false
});

const confirmDialog = ref({
  show: false,
  action: "",
  person: {} as any,
  title: "",
  loading: false
});

const snackbar = ref({
  show: false,
  text: ""
});

const dialogState = ref("");
const person = ref<any>({});
const allPeople = ref<any[]>([]);
const activePeople = ref<any[]>([]);
const archivedPeople = ref<any[]>([]);
const search = ref("");

const headers = computed(() => [
  { title: t("person.name.first"), value: "firstName", width: "20%" },
  { title: t("person.name.last"), value: "lastName", width: "20%" },
  {
    title: t("person.email"),
    value: "email",
    width: "20%",
    class: "hidden-sm-and-down"
  },
  { title: t("person.phone"), value: "phone", width: "20%" },
  { title: t("actions.header"), width: "20%", sortable: false }
]);

const viewOptions = computed(() => [
  { title: t("actions.view-active"), value: "viewActive", class: "view-active" },
  { title: t("actions.view-archived"), value: "viewArchived", class: "view-archived" },
  { title: t("actions.view-all"), value: "viewAll" }
]);

const peopleToDisplay = computed(() => {
  switch (viewStatus.value) {
    case "viewActive":
      return activePeople.value;
    case "viewArchived":
      return archivedPeople.value;
    case "viewAll":
      return allPeople.value;
    default:
      return activePeople.value;
  }
});

watch(
  () => props.peopleList,
  (all_people) => {
    allPeople.value = all_people;
    activePeople.value = allPeople.value.filter(p => p.active);
    archivedPeople.value = allPeople.value.filter(p => !p.active);
  }
);

function editPerson(p: any) {
  dialogState.value = "edit";
  person.value = p;
}

function newPerson() {
  dialogState.value = "new";
}

function cancelPerson() {
  dialogState.value = "";
}

function showSnackbar(message: string) {
  snackbar.value.text = message;
  snackbar.value.show = true;
}

function showConfirmDialog(action: string, p: any) {
  confirmDialog.value.title = "person.messages.confirm." + action;
  confirmDialog.value.action = action;
  confirmDialog.value.person = p;
  confirmDialog.value.show = true;
}

function confirmAction(action: string, p: any) {
  if (action === "deactivate") {
    deactivatePerson(p);
  } else if (action === "activate") {
    activatePerson(p);
  }
}

function cancelAction() {
  confirmDialog.value.show = false;
}

function adminPerson(p: any) {
  adminDialog.value.person = p;
  adminDialog.value.rolesEnabled = false;
  http
    .get(`/api/v1/people/persons/${p.id}`)
    .then(resp => {
      console.log("FETCHED ACCOUNT", resp);
      adminDialog.value.account = resp.data;
      adminDialog.value.show = true;
    })
    .catch(err => console.error("FAILURE", err.response));
}

function closeAdmin() {
  adminDialog.value.show = false;
}

function addAccount(account: any) {
  http
    .post("/api/v1/people/accounts", account)
    .then(resp => {
      console.log("ADDED ACCOUNT", resp);
      refreshPeopleList();
      showSnackbar(t("account.messages.added-ok"));
    })
    .catch(err => console.error("FAILURE", err.response));
}

function updateAccount(accountId: number, account: any) {
  http
    .patch(`/api/v1/people/accounts/${accountId}`, account)
    .then(resp => {
      console.log("PATCHED ACCOUNT", resp);
      refreshPeopleList();
      showSnackbar(t("account.messages.updated-ok"));
    })
    .catch(err => console.error("FAILURE", err.response));
}

function deactivateAccount(accountId: number) {
  http
    .put(`/api/v1/people/accounts/deactivate/${accountId}`)
    .then(resp => {
      console.log("DEACTIVATED ACCOUNT", resp);
      showSnackbar(t("person.messages.account-deactivate"));
    })
    .then(() => refreshPeopleList())
    .catch(err => console.error("FAILURE", err.response));
}

function reactivateAccount(accountId: number) {
  http
    .put(`/api/v1/people/accounts/activate/${accountId}`)
    .then(resp => {
      console.log("REACTIVATED ACCOUNT", resp);
      refreshPeopleList();
      showSnackbar(t("person.messages.account-activate"));
    })
    .catch(err => console.error("FAILURE", err.response));
}

function activatePerson(p: any) {
  http
    .put(`/api/v1/people/persons/activate/${p.id}`)
    .then(resp => {
      console.log("ACTIVATED PERSON", resp);
      showSnackbar(t("person.messages.person-activate"));
    })
    .then(() => refreshPeopleList())
    .catch(err => console.error("FAILURE", err.response))
    .finally(() => {
      confirmDialog.value.loading = false;
      confirmDialog.value.show = false;
    });
}

function deactivatePerson(p: any) {
  http
    .put(`/api/v1/people/persons/deactivate/${p.id}`)
    .then(resp => {
      console.log("DEACTIVATED PERSON", resp);
      showSnackbar(t("person.messages.person-deactivate"));
    })
    .then(() => refreshPeopleList())
    .then(() => {
      if (p.accountInfo && p.accountInfo.active) {
        deactivateAccount(p.accountInfo.id);
      }
    })
    .catch(err => console.error("FAILURE", err.response))
    .finally(() => {
      confirmDialog.value.loading = false;
      confirmDialog.value.show = false;
    });
}

function refreshPeopleList() {
  emit("fetchPeopleList");
}
</script>
