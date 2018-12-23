<template>
  <v-card>
    <v-card-title>
      {{ $t("person.people") }}
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="search"
        v-bind:label="$t('forms.search')"
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
        <td>{{ props.item.firstName }}</td>
        <td>{{ props.item.lastName }}</td>
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
        { text: this.$t("person.gender"), value: "gender" },
        { text: this.$t("person.date.birthday"), value: "birthday" },
        { text: this.$t("person.email"), value: "email" },
        { text: this.$t("person.phone"), value: "phone" }
      ];
    }
  },
  mounted: function() {
    axios.get("/api/v1/people/persons").then(resp => (this.people = resp.data));
  }
};
</script>
