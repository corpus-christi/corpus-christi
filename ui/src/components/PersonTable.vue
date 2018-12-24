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

      <!-- New Person dialog -->
      <v-dialog v-model="showNewPersonDialog" max-width="500px">
        <v-btn slot="activator" color="primary">
          {{ $t("person.actions.new") }}
        </v-btn>
        <PersonForm v-on:cancel="cancel" v-on:save="save" />
      </v-dialog>
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
      </template>
    </v-data-table>
  </div>
</template>

<script>
import axios from "axios";
import PersonForm from "./PersonForm";

export default {
  name: "PersonTable",
  components: { PersonForm },
  data() {
    return {
      showNewPersonDialog: false,

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
        { text: this.$t("person.phone"), value: "phone" }
      ];
    }
  },
  methods: {
    cancel() {
      this.showNewPersonDialog = false;
    },
    save(newPerson) {
      axios
        .post("/api/v1/people/persons", newPerson)
        .then(resp => console.log("SUCCESS", resp))
        .catch(err => console.error("FAILURE", err.response));
    }
  },
  mounted: function() {
    axios.get("/api/v1/people/persons").then(resp => (this.people = resp.data));
  }
};
</script>
