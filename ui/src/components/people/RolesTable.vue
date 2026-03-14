<template>
  <div>
    <!-- Header -->
    <v-toolbar class="pa-1" data-cy="roles-toolbar">
      <v-row align="center" justify="space-between">
        <v-col md="2">
          <v-toolbar-title>{{ t("people.title-roles") }}</v-toolbar-title>
        </v-col>
        <v-col md="3">
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="t('actions.search')"
            hide-details
            clearable
            single-line
            data-cy="roles-search"
          />
        </v-col>
        <v-col md="3">
          <div data-cy="roles-dropdown">
            <v-select
              hide-details
              solo
              single-line
              :label="t('people.title-roles')"
              :items="translatedRoles.concat(viewOption)"
              v-model="viewStatus"
            />
          </div>
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
      data-cy="roles-table"
    >
      <template #item="{ item }">
        <tr>
          <td :data-cy="'first-name-' + item.id">
            {{ item.firstName }}
          </td>
          <td :data-cy="'last-name-' + item.id">
            {{ item.lastName }}
          </td>
          <td :data-cy="'username-' + item.id">
            {{ item.username }}
          </td>
          <td :data-cy="'roles-' + item.id">
            <v-chip v-for="role in item.roles" :key="role.id" size="small">{{
              t(role.nameI18n)
            }}</v-chip>
          </td>
          <td class="text-no-wrap">
            <v-tooltip bottom>
              <template #activator="{ props: tooltipProps }">
                <v-btn
                  icon
                  variant="outlined"
                  size="small"
                  color="primary"
                  v-bind="tooltipProps"
                  v-on:click="adminPerson(item)"
                  data-cy="roles-settings"
                >
                  <v-icon size="small">settings</v-icon>
                </v-btn>
              </template>
              <span>{{ t("actions.tooltips.settings") }}</span>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import PersonAdminForm from "./AccountForm.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;

const props = defineProps<{
  peopleList: any[];
  rolesList: any[];
  tableLoaded: boolean;
}>();

const emit = defineEmits(["fetchPeopleList"]);

const viewStatus = ref<any>("allRoles");
const adminDialog = ref({
  show: false,
  person: {} as any,
  account: {} as any,
  rolesEnabled: false
});

const snackbar = ref({ show: false, text: "" });
const selected = ref<any[]>([]);
const allPeople = ref<any[]>([]);
const search = ref("");

const rolePublic = ref<any[]>([]);
const roleInfrastructure = ref<any[]>([]);
const roleSuperuser = ref<any[]>([]);
const roleTranslator = ref<any[]>([]);
const roleGroupAdmin = ref<any[]>([]);
const roleGroupLeader = ref<any[]>([]);
const roleGroupOverseer = ref<any[]>([]);
const roleRegistrar = ref<any[]>([]);
const roleTeachingAssistant = ref<any[]>([]);
const roleEventPlanner = ref<any[]>([]);
const roleVisitor = ref<any[]>([]);

const headers = computed(() => [
  { title: t("person.name.first"), value: "firstName", width: "15%" },
  { title: t("person.name.last"), value: "lastName", width: "15%" },
  { title: t("person.username"), value: "person.username", width: "15%" },
  { title: t("people.title-roles"), value: "person.roles", width: "35%" },
  { title: t("actions.header"), width: "17%", sortable: false }
]);

const peopleToDisplay = computed(() => {
  switch (viewStatus.value) {
    case 1: return rolePublic.value;
    case 2: return roleInfrastructure.value;
    case 3: return roleSuperuser.value;
    case 4: return roleTranslator.value;
    case 5: return roleGroupAdmin.value;
    case 6: return roleGroupLeader.value;
    case 7: return roleGroupOverseer.value;
    case 8: return roleRegistrar.value;
    case 9: return roleTeachingAssistant.value;
    case 10: return roleEventPlanner.value;
    case 11: return roleVisitor.value;
    case "allRoles":
    default:
      return allPeople.value;
  }
});

const translatedRoles = computed(() => {
  return props.rolesList.map(element => ({
    title: t(element.text),
    value: element.value
  }));
});

const viewOption = computed(() => [
  { title: t("people.dropdown-roles"), value: "allRoles" }
]);

watch(
  () => props.peopleList,
  (all_people) => {
    allPeople.value = all_people;
    rolePublic.value = allPeople.value.filter(p => p.roles.some((role: any) => role.id === 1));
    roleInfrastructure.value = allPeople.value.filter(p => p.roles.some((role: any) => role.id === 2));
    roleSuperuser.value = allPeople.value.filter(p => p.roles.some((role: any) => role.id === 3));
    roleTranslator.value = allPeople.value.filter(p => p.roles.some((role: any) => role.id === 4));
    roleGroupAdmin.value = allPeople.value.filter(p => p.roles.some((role: any) => role.id === 5));
    roleGroupLeader.value = allPeople.value.filter(p => p.roles.some((role: any) => role.id === 6));
    roleGroupOverseer.value = allPeople.value.filter(p => p.roles.some((role: any) => role.id === 7));
    roleRegistrar.value = allPeople.value.filter(p => p.roles.some((role: any) => role.id === 8));
    roleTeachingAssistant.value = allPeople.value.filter(p => p.roles.some((role: any) => role.id === 9));
    roleEventPlanner.value = allPeople.value.filter(p => p.roles.some((role: any) => role.id === 10));
    roleVisitor.value = allPeople.value.filter(p => p.roles.some((role: any) => role.id === 11));
  }
);

function showSnackbar(message: string) {
  snackbar.value.text = message;
  snackbar.value.show = true;
}

function adminPerson(person: any) {
  adminDialog.value.person = person;
  adminDialog.value.rolesEnabled = true;
  http
    .get(`/api/v1/people/persons/${person.id}`)
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

function addAccount(person: any) {
  http
    .post("/api/v1/people/persons", person)
    .then(resp => {
      console.log("Person ADDED", resp);
      refreshPeopleList();
      showSnackbar(t("account.messages.added-ok"));
    })
    .catch(err => console.error("FAILURE", err.response));
}

function updateAccount(personId: number, person: any) {
  http
    .patch(`/api/v1/people/accounts/${personId}`, person)
    .then(resp => {
      console.log("PATCHED ACCOUNT", resp);
      refreshPeopleList();
      showSnackbar(t("account.messages.updated-ok"));
    })
    .catch(err => console.error("FAILURE", err.response));
}

function deactivateAccount(personId: number) {
  http
    .put(`/api/v1/people/accounts/deactivate/${personId}`)
    .then(resp => {
      console.log("DEACTIVATED ACCOUNT", resp);
      showSnackbar(t("person.messages.account-deactivate"));
    })
    .then(() => refreshPeopleList())
    .catch(err => console.error("FAILURE", err.response));
}

function reactivateAccount(personId: number) {
  http
    .put(`/api/v1/people/accounts/activate/${personId}`)
    .then(resp => {
      console.log("REACTIVATED ACCOUNT", resp);
      refreshPeopleList();
      showSnackbar(t("person.messages.account-activate"));
    })
    .catch(err => console.error("FAILURE", err.response));
}

function refreshPeopleList() {
  emit("fetchPeopleList");
}
</script>
