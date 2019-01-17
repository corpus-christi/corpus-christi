<template>
  <div>
    <v-toolbar>
      <v-toolbar-title>{{ $t("courses.students") }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="search"
        v-bind:label="$t('actions.search')"
        single-line
        hide-details
      ></v-text-field>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        r        data-cy="add-student"
      >
        <v-icon dark left>add</v-icon>
        {{ $t("actions.add-person") }}
      </v-btn>
    </v-toolbar>
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
        <td></td>
      </template>
    </v-data-table>
  </div>
</template>

<script>
import EntitySearch from "../EntitySearch";
export default {
  components: { "entity-search": EntitySearch },
  name: "CourseOfferingStudents",
  data() {
    return {
      selectedValue: null,
      search: "",
      students: [],
      people: [],
      newStudent: null,
      newStudentDialog: {
        show: false,
        eventId: -1,
        loading: false
      },
      
    };
  },
  
  props: {
    offeringId: 0
  },
  
  computed: {
    headers() {
      return [
        {
          text: this.$t("person.name.first"),
          value: "firstName",
          width: "20%"
        },
        { text: this.$t("person.name.last"), value: "lastName", width: "20%" },
        { text: this.$t("person.email"), value: "email", width: "22.5%" },
        { text: this.$t("person.phone"), value: "phone", width: "22.5%" },
        { text: this.$t("actions.header"), sortable: false }
      ];
    }
  },

  methods: {
    activateNewStudentDialog(eventId) {
      this.newStudentDialog.show = true;
      this.newStudentDialog.eventId = eventId;
    },
    openStudentDialog(event) {
      this.activateNewStudentDialog(event.id);
    },
    cancelNewStudentDialog() {
      this.newStudentDialog.show = false;
    },
    addStudent() {
      console.log(this.newStudent);
      this.newStudentDialog.loading = true;
      // loading true
      // axios post
      // success -> re-request Students all
      // loading false
      this.newStudentDialog.loading = false;
      this.newStudentDialog.show = false;
      this.newStudent = null;
    },
    archiveStudent() {
      // loading true
      // axios post
      // success -> re-request Students all
      // loading false
    }
  },

  mounted: function() {
    const id = this.offeringId;
    this.$http.get(`/api/v1/courses/course_offerings/${id}/students`).then(resp => {
      this.students = resp.data;

      for (var i = 0; i < this.students.length; i++) {
        this.$http.get(`/api/v1/people/persons/${this.students[i].studentId}`).then(peopleResp => {
          this.people.push(peopleResp.data);
        });
      }
      
    });
  }
};
</script>
