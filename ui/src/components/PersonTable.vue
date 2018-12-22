<template>
  <v-card>
    <v-card-title>
      People
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="search"
        label="Search"
        single-line
        hide-details
      ></v-text-field>
    </v-card-title>

    <v-data-table
      v-model="selected"
      :headers="headers"
      :items="people"
      :search="search"
      select-all
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td>
          <v-checkbox
            v-model="props.selected"
            primary
            hide-details
          ></v-checkbox>
        </td>
        <td>{{ props.item.first_name }}</td>
        <td>{{ props.item.last_name }}</td>
        <td>{{ props.item.gender }}</td>
        <td>{{ props.item.birthday }}</td>
        <td>{{ props.item.email }}</td>
        <td>{{ props.item.phone }}</td>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios";

export default {
  name: "PersonTable",
  data() {
    return {
      headers: [
        { text: this.$t("person.name.first"), value: "first_name" },
        { text: this.$t("person.name.last"), value: "last_name" },
        { text: this.$t("person.gender"), value: "gender" },
        { text: this.$t("person.birthday"), value: "birthday" },
        { text: this.$t("person.email"), value: "email" },
        { text: this.$t("person.phone"), value: "phone" }
      ],
      selected: [],
      people: [],
      search: ""
    };
  },
  mounted: function() {
    axios.get("/api/v1/people/persons").then(resp => (this.people = resp.data));
  }
};
</script>
