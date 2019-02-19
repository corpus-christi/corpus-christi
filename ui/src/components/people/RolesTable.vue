<template>
  <div>
    <!-- Header -->
    <v-toolbar class="pa-1" data-cy="roles-toolbar">
      <v-layout align-center justify-space-between fill-height>
        <v-flex md2>
          <v-toolbar-title>{{ $t("people.title-roles") }}</v-toolbar-title>
        </v-flex>
        <v-flex md3>
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="$t('actions.search')"
            hide-details
            clearable
            single-line
            box
            data-cy="roles-search"
          ></v-text-field>
        </v-flex>
        <v-flex md3>
          <div data-cy="roles-dropdown">
            <v-select
              hide-details
              solo
              single-line
              :label="$t('people.title-roles')"
              :items="translatedRoles"
            ></v-select>
          </div>
        </v-flex>
      </v-layout>
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
      <template slot="items" slot-scope="props">
        <td class="text-xs-center">
          <span v-if="props.item.accountInfo">
            <span v-if="props.item.accountInfo.active">
              <v-tooltip bottom>
                <v-icon size="16" slot="activator" data-cy="account-active-icon"
                  >account_circle</v-icon
                >
                {{ $t("account.active") }}
              </v-tooltip>
            </span>

            <span v-if="!props.item.accountInfo.active">
              <v-tooltip bottom>
                <v-icon
                  size="16"
                  slot="activator"
                  data-cy="account-inactive-icon"
                  >person_outline</v-icon
                >
                {{ $t("account.inactive") }}
              </v-tooltip>
            </span>
          </span>
        </td>
        <td :data-cy="'first-name-' + props.item.id">
          {{ props.item.firstName }}
        </td>
        <td :data-cy="'last-name-' + props.item.id">
          {{ props.item.lastName }}
        </td>
        <td :data-cy="'username-' + props.item.id">
          {{ props.item.accountInfo.username }}
        </td>
        <td :data-cy="'roles-' + props.item.id">
          <v-chip
            v-for="role in props.item.accountInfo.roles"
            :key="role.id"
            small
            >{{ $t(role.nameI18n) }}</v-chip
          >
        </td>

        <td class="text-no-wrap">
          <v-tooltip bottom>
            <v-btn
              icon
              outline
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
      <v-btn flat @click="snackbar.show = false" data-cy>
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
      required: true
    },
    rolesList: {
      type: Array,
      required: true
    },
    tableLoaded: Boolean
  },

  data() {
    return {
      personRoles: [],
      personDialog: {
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        attributes: [],
        person: {}
      },

      adminDialog: {
        show: false,
        person: {},
        account: {},
        rolesEnabled: false
      },

      snackbar: {
        show: false,
        text: ""
      },

      showingArchived: false,
      selected: [],
      allPeople: [],
      allAccount: [],
      search: "",
      data: {}
    };
  },
  computed: {
    // Put here so that the headers are reactive.
    headers() {
      return [
        {
          text: this.$t("person.account"),
          value: "person.accountInfo",
          align: "center",
          width: "3%",
          sortable: false
        },
        {
          text: this.$t("person.name.first"),
          value: "firstName",
          width: "15%"
        },
        { text: this.$t("person.name.last"), value: "lastName", width: "15%" },
        {
          text: this.$t("account.username"),
          value: "accountInfo.username",
          width: "15%"
        },
        {
          text: this.$t("people.title-roles"),
          value: "accountInfo.roles",
          width: "35%"
        },
        { text: this.$t("actions.header"), width: "17%", sortable: false }
      ];
    },
    peopleToDisplay() {
      return this.allAccount;
    },
    translatedRoles() {
      return this.rolesList.map(element => {
        return {
          text: this.$t(element.text),
          value: element.value
        };
      });
    }
  },

  watch: {
    peopleList(all_people) {
      this.allPeople = all_people;
      this.allAccount = this.allPeople.filter(
        person => person.accountInfo && person.active
      );
    },
    rolesList(all_roles) {
      this.rolesList = all_roles;
    },
    tableLoaded(loading) {
      this.tableLoaded = loading;
    }
  },

  methods: {
    // ---- Person Administration

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
        .get(`/api/v1/people/persons/${person.id}/account`)
        .then(resp => {
          console.log("FETCHED ACCOUNT", resp);
          this.adminDialog.account = resp.data;
          this.adminDialog.show = true;
        })
        .catch(err => console.error("FAILURE", err.response));
    },
    closeAdmin() {
      this.adminDialog.show = false;
    },

    addAccount(account) {
      this.$http
        .post("/api/v1/people/accounts", account)
        .then(resp => {
          console.log("ADDED ACCOUNT", resp);
          this.refreshPeopleList();
          this.showSnackbar(this.$t("account.messages.added-ok"));
        })
        .catch(err => console.error("FAILURE", err.response));
    },

    updateAccount(accountId, account) {
      this.$http
        .patch(`/api/v1/people/accounts/${accountId}`, account)
        .then(resp => {
          console.log("PATCHED ACCOUNT", resp);
          this.refreshPeopleList();
          this.showSnackbar(this.$t("account.messages.updated-ok"));
        })
        .catch(err => console.error("FAILURE", err.response));
    },

    deactivateAccount(accountId) {
      this.$http
        .put(`/api/v1/people/accounts/deactivate/${accountId}`)
        .then(resp => {
          console.log("DEACTIVATED ACCOUNT", resp);
          this.showSnackbar(this.$t("person.messages.account-deactivate"));
        })
        .then(() => this.refreshPeopleList())
        .catch(err => console.error("FAILURE", err.response));
    },

    reactivateAccount(accountId) {
      this.$http
        .put(`/api/v1/people/accounts/activate/${accountId}`)
        .then(resp => {
          console.log("REACTIVATED ACCOUNT", resp);
          this.refreshPeopleList();
          this.showSnackbar(this.$t("person.messages.account-activate"));
        })
        .catch(err => console.error("FAILURE", err.response));
    },

    getAttributesInfo() {
      this.$http
        .get("/api/v1/people/persons/fields")
        .then(resp => {
          console.log("FETCHED ATTRIBUTES", resp);
          if (resp.data.person_attributes) {
            this.personDialog.attributes = resp.data.person_attributes;
          }
        })
        .catch(err => console.error("FAILURE", err.response));
    },

    refreshPeopleList() {
      this.$emit("fetchPeopleList");
    }
  }
};
</script>
