<template>
  <div>
    <!-- Header -->
    <v-toolbar class="pa-1">
      <v-layout align-center justify-space-between fill-height>
        <v-flex md2> <v-toolbar-title>$tRoles</v-toolbar-title> </v-flex>
        <v-flex md3>
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="$t('actions.search')"
            hide-details
            clearable
            single-line
            box
            data-cy="search"
          ></v-text-field>
        </v-flex>
        <v-flex md3>
          <div data-cy="view-dropdown">
            <v-select
              hide-details
              solo
              single-line
              :items="rolesList"
              v-model="viewStatus"
            >
            </v-select>
          </div>
        </v-flex>
      </v-layout>
    </v-toolbar>

    <!-- Table of existing people -->
    <v-data-table
      :headers="headers"
      :items="peopleToDisplay"
      :search="search"
      class="elevation-1"
      data-cy="person-table"
    >
      <template slot="items" slot-scope="props">
        <td>
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
        <td class="hidden-sm-and-down" :data-cy="'email-' + props.item.id">
          {{ props.item.email }}
        </td>
        <!-- <td :data-cy="'phone-' + props.item.id">{{ props.item.phone }}</td> -->
        <td class="hidden-sm-and-down" :data-cy="'username-' + props.item.id">
          {{ props.item.accountInfo.username}}
        </td>
          
        <td class="text-no-wrap">
          <!-- <v-tooltip bottom>
            <v-btn
              icon
              outline
              small
              color="primary"
              slot="activator"
              v-on:click="editPerson(props.item)"
              data-cy="edit-person"
            >
              <v-icon small>edit</v-icon>
            </v-btn>
            <span>{{ $t("actions.edit") }}</span>
          </v-tooltip> -->
          <v-tooltip bottom>
            <v-btn
              icon
              outline
              small
              color="primary"
              slot="activator"
              v-on:click="adminPerson(props.item)"
              data-cy="account-settings"
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

    <!-- New/Edit dialog -->
    <v-dialog
      scrollable
      persistent
      v-model="personDialog.show"
      max-width="500px"
    >
      <PersonForm
        v-bind:editMode="personDialog.editMode"
        v-bind:initialData="personDialog.person"
        v-bind:saveLoading="personDialog.saveLoading"
        v-bind:addMoreLoading="personDialog.addMoreLoading"
        v-bind:attributes="personDialog.attributes"
        v-on:cancel="cancelPerson"
        v-on:save="savePerson"
        v-on:add-another="addAnother"
      />
    </v-dialog>

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
import PersonForm from "./PersonForm";
import PersonAdminForm from "./AccountForm";

export default {
  name: "RolesTable",
  components: { PersonAdminForm, PersonForm },
  props: {
    peopleList: {
      type: Array,
      required: true
    },
    rolesList: {
      type: Array,
      required: true
    },
  },
  
  data() {
    return {
      viewStatus: "viewActive",
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
        roles: []
      },

      snackbar: {
        show: false,
        text: ""
      },

      showingArchived: false,
      selected: [],
      allPeople: [],
      activePeople: [],
      allAccount: [],
      archivedPeople: [],
      // rolesList: [],
      search: "",
      data: {}
    };
  },
  computed: {
    // Put here so that the headers are reactive.
    headers() {
      return [
        {
          text: "Account",
          value: "person.accountInfo",
          align: "left",
          sortable: false
        },
        {
          text: this.$t("person.name.first"),
          value: "firstName",
          width: "10%"
        },
        { text: this.$t("person.name.last"), value: "lastName", width: "20%" },
        {
          text: this.$t("person.email"),
          value: "email",
          width: "15%",
          class: "hidden-sm-and-down"
        },
        { text: this.$t("person.accountInfo.username"), value: "username", width: "15%" },
        { text: this.$t("actions.header"), sortable: false }
      ];
    },
    viewOptions() {
      return [
        {
          text: this.$t("actions.view-active"),
          value: "viewActive",
          class: "view-active"
        },
        {
          text: this.$t("actions.view-archived"),
          value: "viewArchived",
          class: "view-archived"
        },
        { text: this.$t("actions.view-all"), value: "viewAll" }
      ];
    },
    peopleToDisplay() {
      // switch (this.viewStatus) {
      //   case "viewActive":
      //     return this.activePeople;
      //   case "viewArchived":
      //     return this.archivedPeople;
      //   case "viewAll":
      //     return this.allPeople;
      //   default:
      //     return this.activePeople;
      return this.allAccount;
      // }
    }
  },

  watch: {
    peopleList(all_people) {
    this.allPeople = all_people;
    this.allAccount = this.allPeople.filter(person => person.accountInfo);
    },

    rolesList(all_roles) {
      console.log(this.rolesList);
      this.rolesList = all_roles;
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

    savePerson(person) {
      this.personDialog.saveLoading = true;
      if (this.personDialog.editMode) {
        // Hang on to the ID of the person being updated.
        const person_id = person.id;
        // Locate the person we're updating in the table.
        const idx = this.allPeople.findIndex(p => p.id === person.id);
        // Get rid of the ID; not for consumption by endpoint.
        delete person.id;

        console.log(person);
        this.data = this.constructPersonData(person);
        console.log(this.data);
        this.$http
          .put(`/api/v1/people/persons/${person_id}`, this.data)
          .then(resp => {
            console.log("EDITED", resp);
            Object.assign(this.allPeople[idx], person);
            this.personDialog.show = false;
            this.personDialog.saveLoading = false;
            this.showSnackbar(this.$t("person.messages.person-edit"));
          })
          .catch(err => {
            console.error("FALURE", err.response);
            this.personDialog.saveLoading = false;
            this.showSnackbar(this.$t("person.messages.person-save-error"));
          });
      } else {
        console.log(person);
        this.data = this.constructPersonData(person);
        console.log(this.data);
        this.$http
          .post("/api/v1/people/persons", this.data)
          .then(resp => {
            console.log("ADDED", resp);
            this.refreshPeopleList();
            this.personDialog.show = false;
            this.personDialog.saveLoading = false;
            this.showSnackbar(this.$t("person.messages.person-add"));
          })
          .catch(err => {
            console.error("FAILURE", err.response);
            this.personDialog.saveLoading = false;
            this.showSnackbar(this.$t("person.messages.person-save-error"));
          });
      }
    },

    constructPersonData(person) {
      var attributes = [];
      if (person.attributesInfo) {
        attributes = person.attributesInfo;
      }
      delete person["attributesInfo"];
      delete person["accountInfo"];
      return {
        person: person,
        attributesInfo: attributes
      };
    },

    addAnother(person) {
      this.personDialog.addMoreLoading = true;
      this.data = this.constructPersonData(person);
      this.$http
        .post("/api/v1/people/persons", this.data)
        .then(resp => {
          console.log("ADDED", resp);
          this.refreshPeopleList();
          this.activatePersonDialog();
          this.personDialog.addMoreLoading = false;
          this.showSnackbar(this.$t("person.messages.person-add"));
        })
        .catch(err => {
          console.error("FAILURE", err.response);
          this.personDialog.addMoreLoading = false;
          this.showSnackbar(this.$t("person.messages.person-save-error"));
        });
    },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },

    // ---- Account Administration

    adminPerson(person) {
      // Pass along the current person.
      this.adminDialog.person = person;
      // Fetch the person's account information (if any) before activating the dialog.
      this.$http
        .get(`/api/v1/people/persons/${person.id}/account`)
        .then(resp => {
          console.log("FETCHED", resp);
          this.adminDialog.account = resp.data;
          this.adminDialog.roles = this.rolesList;
          this.adminDialog.show = true;
        })
        .catch(err => console.error("FAILURE Haaha", err.response));
    },
    closeAdmin() {
      this.adminDialog.show = false;
    },

    addAccount(account) {
      this.$http
        .post("/api/v1/people/accounts", account)
        .then(resp => {
          console.log("ADDED", resp);
          this.refreshPeopleList();
          this.showSnackbar(this.$t("account.messages.added-ok"));
        })
        .catch(err => console.error("FAILURE", err.response));
    },

    updateAccount(accountId, account) {
      this.$http
        .patch(`/api/v1/people/accounts/${accountId}`, account)
        .then(resp => {
          console.log("PATCHED", resp);
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

    activatePerson(person) {
      this.$http
        .put(`/api/v1/people/persons/activate/${person.id}`)
        .then(resp => {
          console.log("ACTIVATED PERSON", resp);
          this.showSnackbar(this.$t("person.messages.person-activate"));
        })
        .then(() => this.refreshPeopleList())
        .catch(err => console.error("FAILURE", err.response));
    },

    deactivatePerson(person) {
      this.$http
        .put(`/api/v1/people/persons/deactivate/${person.id}`)
        .then(resp => {
          console.log("DEACTIVATED PERSON", resp);
          this.showSnackbar(this.$t("person.messages.person-deactivate"));
        })
        .then(() => this.refreshPeopleList())
        .then(() => {
          if (person.accountInfo && person.accountInfo.active) {
            this.deactivateAccount(person.accountInfo.id);
          }
        })
        .catch(err => console.error("FAILURE PLEASE", err.response));
    },

    getAttributesInfo() {
      this.$http
        .get("/api/v1/people/persons/fields")
        .then(resp => {
          if (resp.data.person_attributes) {
            this.personDialog.attributes = resp.data.person_attributes;
          }
        })
        .catch(err => console.error("FAILURE", err.response));
    },

    refreshPeopleList() {
      this.$emit("fetchPeopleList")
    },
  },

  mounted: function() {
    this.getAttributesInfo();
  }
};
/*
@TODO:
  Make the search be able to use username as a search parameter.
*/
</script>
