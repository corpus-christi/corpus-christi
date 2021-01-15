<template>
  <div>
    <!-- Header -->
    <v-toolbar data-cy="roles-toolbar">
      <v-row align="center" justify="space-between">
        <v-col cols="2">
          <v-toolbar-title>{{ $t("people.title-roles") }}</v-toolbar-title>
        </v-col>
        <v-col cols="6">
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="$t('actions.search')"
            hide-details
            clearable
            single-line
            filled
            data-cy="roles-search"
          />
        </v-col>
        <v-col cols="2">
          <div data-cy="roles-dropdown">
            <v-select
              hide-details
              solo
              single-line
              :label="$t('people.title-roles')"
              :items="translatedRoles.concat(viewOption)"
              v-model="viewStatus"
            />
          </div>
        </v-col>
      </v-row>
    </v-toolbar>

    <!-- Table -->
    <v-data-table
      :headers="headers"
      :items="peopleToDisplay"
      :search="search"
      :loading="!tableLoaded"
      class="elevation-1"
      data-cy="roles-table"
    >
      <template slot="items" slot-scope="props">
        <td :data-cy="'first-name-' + props.item.id">
          {{ props.item.firstName }}
        </td>
        <td :data-cy="'last-name-' + props.item.id">
          {{ props.item.lastName }}
        </td>
        <td :data-cy="'username-' + props.item.id">
          {{ props.item.username }}
        </td>
        <td :data-cy="'roles-' + props.item.id">
          <v-chip v-for="role in props.item.roles" :key="role.id" small>{{
            $t(role.nameI18n)
          }}</v-chip>
        </td>

        <td class="text-no-wrap">
          <v-tooltip bottom>
            <v-btn
              icon
              outlined
              small
              color="primary"
              slot="activator"
              v-on:click="adminPerson(props.item)"
              data-cy="roles-settings"
            >
              <v-icon small>settings</v-icon>
            </v-btn>
            <span>{{ $t("actions.tooltips.settings") }}</span>
          </v-tooltip>
        </td>
      </template>
    </v-data-table>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn text @click="snackbar.show = false" data-cy>
        {{ $t("actions.close") }}
      </v-btn>
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

<script>
import PersonAdminForm from "./AccountForm";

export default {
  name: "RolesTable",
  components: { PersonAdminForm },
  props: {
    peopleList: {
      type: Array,
      required: true,
    },
    rolesList: {
      type: Array,
      required: true,
    },
    tableLoaded: Boolean,
  },

  data() {
    return {
      viewStatus: this.allPeople,
      personRoles: [],
      personDialog: {
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        attributes: [],
        person: {},
      },

      adminDialog: {
        show: false,
        person: {},
        account: {},
        rolesEnabled: false,
      },

      snackbar: {
        show: false,
        text: "",
      },

      showingArchived: false,
      selected: [],
      allPeople: [],
      search: "",
      data: {},
    };
  },
  computed: {
    // Put here so that the headers are reactive.
    headers() {
      return [
        {
          text: this.$t("person.name.first"),
          value: "firstName",
          width: "15%",
        },
        { text: this.$t("person.name.last"), value: "lastName", width: "15%" },
        {
          text: this.$t("person.username"),
          value: "person.username",
          width: "15%",
        },
        {
          text: this.$t("people.title-roles"),
          value: "person.roles",
          width: "35%",
        },
        { text: this.$t("actions.header"), width: "17%", sortable: false },
      ];
    },
    peopleToDisplay() {
      switch (this.viewStatus) {
        case 1:
          return this.rolePublic;
        case 2:
          return this.roleInfrastructure;
        case 3:
          return this.roleSuperuser;
        case 4:
          return this.roleTranslator;
        case 5:
          return this.roleGroupAdmin;
        case 6:
          return this.roleGroupLeader;
        case 7:
          return this.roleGroupOverseer;
        case 8:
          return this.roleRegistrar;
        case 9:
          return this.roleTeachingAssistant;
        case 10:
          return this.roleEventPlanner;
        case 11:
          return this.roleVisitor;
        case "allRoles":
          return this.allPeople;
        default:
          return this.allPeople;
      }
    },

    translatedRoles() {
      return this.rolesList.map((element) => {
        return {
          text: this.$t(element.text),
          value: element.value,
        };
      });
    },

    viewOption() {
      return [
        {
          text: this.$t("people.dropdown-roles"),
          value: "allRoles",
        },
      ];
    },
  },

  watch: {
    //This needs cleaned up in the future
    peopleList(all_people) {
      this.allPeople = all_people;
      this.rolePublic = this.allPeople.filter((person) =>
        person.roles.some((role) => role.id === 1)
      );
      this.roleInfrastructure = this.allPeople.filter((person) =>
        person.roles.some((role) => role.id === 2)
      );
      this.roleSuperuser = this.allPeople.filter((person) =>
        person.roles.some((role) => role.id === 3)
      );
      this.roleTranslator = this.allPeople.filter((person) =>
        person.roles.some((role) => role.id === 4)
      );
      this.roleGroupAdmin = this.allPeople.filter((person) =>
        person.roles.some((role) => role.id === 5)
      );
      this.roleGroupLeader = this.allPeople.filter((person) =>
        person.roles.some((role) => role.id === 6)
      );
      this.roleGroupOverseer = this.allPeople.filter((person) =>
        person.roles.some((role) => role.id === 7)
      );
      this.roleRegistrar = this.allPeople.filter((person) =>
        person.roles.some((role) => role.id === 8)
      );
      this.roleTeachingAssistant = this.allPeople.filter((person) =>
        person.roles.some((role) => role.id === 9)
      );
      this.roleEventPlanner = this.allPeople.filter((person) =>
        person.roles.some((role) => role.id === 10)
      );
      this.roleVisitor = this.allPeople.filter((person) =>
        person.roles.some((role) => role.id === 11)
      );
    },
    // tableLoaded(loading) {
    //   this.tableLoaded = loading;
    // },
  },

  methods: {
    // ---- Person Administration
    verifyPublicRole() {},

    activatePersonDialog(person = {}, editMode = false) {
      this.personDialog.editMode = editMode;
      this.personDialog.person = person;
      this.personDialog.show = true;
    },

    editPerson(person) {
      this.activatePersonDialog({ ...person }, true);
    },

    newPerson() {
      this.activatePersonDialog();
    },

    cancelPerson() {
      this.personDialog.show = false;
    },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },

    // ---- Account Administration

    adminPerson(person) {
      // Pass along the current person.
      this.adminDialog.person = person;
      this.adminDialog.rolesEnabled = true;
      // Fetch the person's account information (if any) before activating the dialog.
      this.$http
        .get(`/api/v1/people/persons/${person.id}`)
        .then((resp) => {
          console.log("FETCHED ACCOUNT", resp);
          this.adminDialog.account = resp.data;
          this.adminDialog.show = true;
        })
        .catch((err) => console.error("FAILURE", err.response));
    },
    closeAdmin() {
      this.adminDialog.show = false;
    },

    addAccount(person) {
      this.$http
        .post("/api/v1/people/persons", person)
        .then((resp) => {
          console.log("Person ADDED", resp);
          this.refreshPeopleList();
          this.showSnackbar(this.$t("account.messages.added-ok"));
        })
        .catch((err) => console.error("FAILURE", err.response));
    },

    updateAccount(personId, person) {
      this.$http
        .patch(`/api/v1/people/accounts/${personId}`, person)
        .then((resp) => {
          console.log("PATCHED ACCOUNT", resp);
          this.refreshPeopleList();
          this.showSnackbar(this.$t("account.messages.updated-ok"));
        })
        .catch((err) => console.error("FAILURE", err.response));
    },

    deactivateAccount(personId) {
      this.$http
        .put(`/api/v1/people/accounts/deactivate/${personId}`)
        .then((resp) => {
          console.log("DEACTIVATED ACCOUNT", resp);
          this.showSnackbar(this.$t("person.messages.account-deactivate"));
        })
        .then(() => this.refreshPeopleList())
        .catch((err) => console.error("FAILURE", err.response));
    },

    reactivateAccount(personId) {
      this.$http
        .put(`/api/v1/people/accounts/activate/${personId}`)
        .then((resp) => {
          console.log("REACTIVATED ACCOUNT", resp);
          this.refreshPeopleList();
          this.showSnackbar(this.$t("person.messages.account-activate"));
        })
        .catch((err) => console.error("FAILURE", err.response));
    },

    getAttributesInfo() {
      this.$http
        .get("/api/v1/people/persons/fields")
        .then((resp) => {
          console.log("FETCHED ATTRIBUTES", resp);
          if (resp.data.person_attributes) {
            this.personDialog.attributes = resp.data.person_attributes;
          }
        })
        .catch((err) => console.error("FAILURE", err.response));
    },

    refreshPeopleList() {
      this.$emit("fetchPeopleList");
    },
  },
};
</script>
