<template>
  <div>
    <!-- Header -->
    <v-toolbar>
      <v-toolbar-title> {{ $t("person.people") }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="search"
        v-bind:label="$t('actions.search')"
        single-line
        hide-details
      ></v-text-field>

      <v-btn color="primary" v-on:click.stop="newPerson()">
        {{ $t("person.actions.new") }}
      </v-btn>
    </v-toolbar>

    <!-- Table of existing people -->
    <v-data-table
      :headers="headers"
      :items="people"
      :search="search"
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td>{{ props.item.firstName }}</td>
        <td>{{ props.item.lastName }}</td>
        <td>{{ props.item.email }}</td>
        <td>{{ props.item.phone }}</td>
        <td>
          <v-tooltip bottom>
            <v-icon
              small
              slot="activator"
              v-on:click="editPerson(props.item)"
              class="mr-3"
            >
              edit
            </v-icon>
            <span>{{ $t("actions.edit") }}</span>
          </v-tooltip>
          <v-tooltip bottom>
            <v-icon
              small
              slot="activator"
              v-on:click="adminPerson(props.item)"
              class="mr-3"
            >
              settings
            </v-icon>
            <span>{{ $t("actions.tooltips.settings") }}</span>
          </v-tooltip>
          <v-tooltip bottom>
            <v-icon
              small
              slot="activator"
              v-on:click="deletePerson(props.item)"
              class="mr-3"
            >
              delete
            </v-icon>
            <span>{{ $t("actions.tooltips.deactivate") }}</span>
          </v-tooltip>
        </td>
      </template>
    </v-data-table>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false">
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>

    <!-- New/Edit dialog -->
    <v-dialog v-model="personDialog.show" max-width="500px">
      <PersonForm
        v-bind:editMode="personDialog.editMode"
        v-bind:initialData="personDialog.person"
        v-on:cancel="cancelPerson"
        v-on:save="savePerson"
      />
    </v-dialog>

    <!-- Person admin dialog -->
    <v-dialog v-model="adminDialog.show" max-width="500px">
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
      personDialog: {
        show: false,
        editMode: false,
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

      selected: [],
      people: [],
      search: ""
    };
  },
  computed: {
    // Put here so that the headers are reactive.
    headers() {
      return [
        { text: this.$t("person.name.first"), value: "firstName" },
        { text: this.$t("person.name.last"), value: "lastName" },
        { text: this.$t("person.email"), value: "email" },
        { text: this.$t("person.phone"), value: "phone" },
        { text: this.$t("actions.header"), sortable: false }
      ];
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
      if (this.personDialog.editMode) {
        // Hang on to the ID of the person being updated.
        const person_id = person.id;
        // Locate the person we're updating in the table.
        const idx = this.people.findIndex(p => p.id === person.id);
        // Get rid of the ID; not for consumption by endpoint.
        delete person.id;

        this.$http
          .put(`/api/v1/people/persons/${person_id}`, person)
          .then(resp => {
            console.log("EDITED", resp);
            Object.assign(this.people[idx], person);
          })
          .catch(err => console.error("FALURE", err.response));
      } else {
        this.$http
          .post("/api/v1/people/persons", person)
          .then(resp => {
            console.log("ADDED", resp);
            this.people.push(resp.data);
          })
          .catch(err => console.error("FAILURE", err.response));
      }
      this.personDialog.show = false;
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
          this.snackbar.text = this.$t("account.messages.added-ok");
          this.snackbar.show = true;
        })
        .catch(err => console.error("FAILURE", err.response));
    },

    updateAccount(accountId, account) {
      this.$http
        .patch(`/api/v1/people/accounts/${accountId}`, account)
        .then(resp => {
          console.log("PATCHED", resp);
          this.snackbar.text = this.$t("account.messages.updated-ok");
          this.snackbar.show = true;
        })
        .catch(err => console.error("FAILURE", err.response));
    }
  },

  mounted: function() {
    this.$http
      .get("/api/v1/people/persons")
      .then(resp => (this.people = resp.data));
  }
};
</script>
