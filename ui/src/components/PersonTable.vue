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

      <!-- New/Edit dialog and button -->
      <v-btn color="primary" v-on:click.stop="newPerson()">
        {{ $t("person.actions.new") }}
      </v-btn>

      <v-dialog v-model="dialog.show" max-width="500px">
        <PersonForm
          v-bind:editMode="dialog.editMode"
          v-bind:initialData="dialog.person"
          v-on:cancel="cancel"
          v-on:save="save"
        />
      </v-dialog>
    </v-toolbar>

    <Snackbar v-if="snackbar.show" v-on:close="snackbar.show = false">
      {{ snackbar.text }}
    </Snackbar>

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
        <td class="justify-center layout px-0">
          <v-icon small v-on:click="editPerson(props.item)" class="mr-3">
            edit
          </v-icon>
          <v-icon small v-on:click="deletePerson(props.item)"> delete </v-icon>
        </td>
      </template>
    </v-data-table>
  </div>
</template>

<script>
import axios from "axios";
import PersonForm from "./PersonForm";
import Snackbar from "./Snackbar";

export default {
  name: "PersonTable",
  components: { Snackbar, PersonForm },
  data() {
    return {
      dialog: {
        show: false,
        editMode: false,
        person: {}
      },

      snackbar: {
        text: "",
        show: false
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
    activateDialog(person = {}, editMode = false) {
      this.dialog.editMode = editMode;
      this.dialog.person = person;
      this.dialog.show = true;
    },

    editPerson(person) {
      this.activateDialog({ ...person }, true);
    },

    newPerson() {
      this.activateDialog();
    },

    showSnackbar(text) {
      this.snackbar.text = text;
      this.snackbar.show = true;
    },

    cancel() {
      this.dialog.show = false;
      this.showSnackbar(this.$t("person.messages.canceled"));
    },

    save(person) {
      if (this.dialog.editMode) {
        // Hang on to the ID of the person being updated.
        const person_id = person.id;
        // Locate the person we're updating in the table.
        const idx = this.people.findIndex(p => p.id === person.id);
        // Get rid of the ID; not for consumption by endpoint.
        delete person.id;

        axios
          .put(`/api/v1/people/persons/${person_id}`, person)
          .then(resp => {
            console.log("EDITED", resp);
            Object.assign(this.people[idx], person);
          })
          .catch(err => console.error("FALURE", err.response));
      } else {
        axios
          .post("/api/v1/people/persons", person)
          .then(resp => {
            console.log("ADDED", resp);
            this.people.push(resp.data);
          })
          .catch(err => console.error("FAILURE", err.response));
      }
      this.dialog.show = false;
    }
  },

  mounted: function() {
    axios.get("/api/v1/people/persons").then(resp => (this.people = resp.data));
  }
};
</script>
