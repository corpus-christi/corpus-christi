<template>
  <div>
    <!-- Header -->
    <v-toolbar>
      <v-layout align-center justify-space-between fill-height>
        <v-flex md2>
          <v-toolbar-title>{{ $t("transcripts.transcript") }}</v-toolbar-title>
        </v-flex>
        <v-spacer></v-spacer>
        <v-flex md3>
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="$t('actions.search')"
            single-line
            hide-details
            data-cy="transcripts-table-search"
          ></v-text-field>
        </v-flex>
        <!--
              possibly filter by active/inactive flag on students...but not for now
            <v-spacer></v-spacer>
            <v-flex md3>
              <v-select
                v-model="viewStatus"
                :items="options"
                solo
                hide-details
                data-cy="transcripts-table-viewstatus"
              ></v-select>
            </v-flex>
            -->
      </v-layout>
    </v-toolbar>

    <!-- Table of existing students -->
    <v-data-table
      :headers="headers"
      :items="showStudents"
      :loading="!tableLoaded"
      :search="search"
      class="elevation-1"
      data-cy="transcripts-table"
    >
      <template slot="items" slot-scope="props">
        <tr>
          <td class="hover-hand" @click="clickThrough(props.item)">
            {{ props.item.lastName }}
          </td>
          <td class="hover-hand" @click="clickThrough(props.item)">
            {{ props.item.firstName }}
          </td>
        </tr>
      </template>
    </v-data-table>
  </div>
</template>

<script>
export default {
  name: "TranscriptsTable",
  components: {},
  data() {
    return {
      tableLoaded: false,
      selected: [],
      students: [],
      search: "",
      viewStatus: "active"
    };
  },
  computed: {
    // Put here so that the headers are reactive.
    headers() {
      return [
        { text: this.$t("person.name.last"), value: "lastName", width: "40%" },
        { text: this.$t("person.name.first"), value: "firstName", width: "60%" } //,
        //{ text: this.$t("actions.header"), sortable: false }
      ];
    },
    /*
    // possibly filter by active/inactive flag on students...but not for now
    options() {
      return [
        { text: this.$t("actions.view-active"), value: "active" },
        { text: this.$t("actions.view-archived"), value: "archived" },
        { text: this.$t("actions.view-all"), value: "all" }
      ];
    },
    */
    showStudents() {
      return this.students;
      /*
      // possibly filter by active/inactive flag on students...but not for now
      switch (this.viewStatus) {
        case "active":
          return this.students.filter(student => student.active);
        case "archived":
          return this.students.filter(student => !student.active);
        case "all":
        default:
          return this.students;
      }
      */
    }
  },
  methods: {
    clickThrough(transcript) {
      console.log(transcript);
      this.$router.push({
        name: "transcript-details",
        params: { studentId: transcript.id }
      });
    }
  },
  mounted: function() {
    console.log("about to fetch students....");
    this.$http.get("/api/v1/courses/students").then(resp => {
      this.students = resp.data;
      console.log("student list received: ", this.students);
      this.tableLoaded = true;
    });
  }
};
</script>

<style scoped>
.hover-hand {
  cursor: pointer;
}
</style>
