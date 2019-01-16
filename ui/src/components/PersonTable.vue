<template>
  <div>
    <!-- Header -->
    <v-toolbar class="pa-1">
      <v-layout align-center justify-space-between fill-height>
        <v-flex md2>
          <v-toolbar-title>{{ $t("people.title") }}</v-toolbar-title>
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
            data-cy="search"
          ></v-text-field>
        </v-flex>
        <v-flex md3>
          <div data-cy="view-dropdown">
            <v-select
              hide-details
              solo
              single-line
              :items="viewOptions"
              v-model="viewStatus"
            >
            </v-select>
          </div>
        </v-flex>
        <v-flex shrink justify-self-end>
          <v-btn
            class="mr-0 ml-0"
            color="primary"
            raised
            v-on:click.stop="newPerson"
            data-cy="new-person"
          >
            <v-icon left>person_add</v-icon>
            {{ $t("actions.add-person") }}
          </v-btn>
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
          <v-icon size="15" v-if="props.item.accountInfo"
            >account_circle</v-icon
          >
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
        <td :data-cy="'phone-' + props.item.id">{{ props.item.phone }}</td>
        <td class="text-no-wrap">
          <v-tooltip bottom>
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
          </v-tooltip>
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
          <v-tooltip bottom>
            <v-btn
              v-if="props.item.active === true"
              icon
              outline
              small
              color="primary"
              slot="activator"
              v-on:click="deactivatePerson(props.item)"
              data-cy="deactivate-person"
            >
              <v-icon small>archive</v-icon>
            </v-btn>
            <span>{{ $t("actions.tooltips.archive") }}</span>
          </v-tooltip>
          <v-tooltip bottom>
            <v-btn
              v-if="props.item.active === false"
              icon
              outline
              small
              color="primary"
              slot="activator"
              v-on:click="activatePerson(props.item)"
              data-cy="deactivate-person"
            >
              <v-icon small>undo</v-icon>
            </v-btn>
            <span>{{ $t("actions.tooltips.activate") }}</span>
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
    <v-dialog scrollable v-model="personDialog.show" max-width="500px">
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
    <v-dialog scrollable v-model="adminDialog.show" max-width="500px">
      <PersonAdminForm
        v-bind:person="adminDialog.person"
        v-bind:account="adminDialog.account"
        v-on:addAccount="addAccount"
        v-on:updateAccount="updateAccount"
        v-on:close="closeAdmin"
      />
    </v-dialog>
  </div>
</template>

<script>
import PersonForm from "./PersonForm";
import PersonAdminForm from "./AccountForm";

export default {
  name: "PersonTable",
  components: { PersonAdminForm, PersonForm },
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
        account: {}
      },

      snackbar: {
        show: false,
        text: ""
      },

      showingArchived: false,
      selected: [],
      allPeople: [],
      activePeople: [],
      archivedPeople: [],
      search: "",
      data: {}
    };
  },
  computed: {
    // Put here so that the headers are reactive.
    headers() {
      return [
        {
          text: "",
          value: "person.accountInfo",
          align: "right",
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
        { text: this.$t("person.phone"), value: "phone", width: "15%" },
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
      switch (this.viewStatus) {
        case "viewActive":
          return this.activePeople;
        case "viewArchived":
          return this.archivedPeople;
        case "viewAll":
          return this.allPeople;
        default:
          return this.activePeople;
      }
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
      this.$http
        .post("/api/v1/people/persons", person)
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
          console.log("ADDED", resp);
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

    activatePerson(person) {
      this.$http
        .put(`/api/v1/people/persons/activate/${person.id}`)
        .then(resp => {
          console.log("ACTIVATED", resp);
          this.showSnackbar(this.$t("person.messages.person-activate"));
        })
        .then(() => this.refreshPeopleList())
        .catch(err => console.error("FAILURE", err.response));
    },

    deactivatePerson(person) {
      this.$http
        .put(`/api/v1/people/persons/deactivate/${person.id}`)
        .then(resp => {
          console.log("DEACTIVATED", resp);
          this.showSnackbar(this.$t("person.messages.person-deactivate"));
        })
        .then(() => this.refreshPeopleList())
        .catch(err => console.error("FAILURE", err.response));
    },

    refreshPeopleList() {
      this.$http
        .get("/api/v1/people/persons")
        .then(resp => {
          this.allPeople = resp.data;
          this.activePeople = this.allPeople.filter(person => person.active);
          this.archivedPeople = this.allPeople.filter(person => !person.active);
        })
        .catch(err => console.error("FAILURE", err.response));
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
    }
  },

  mounted: function() {
    this.refreshPeopleList();
    this.getAttributesInfo();
  }
};
</script>
