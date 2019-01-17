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
      <v-btn color="primary" raised v-on:click.stop="newStudent">
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
        <td>
          <StudentsAdminActions
            v-bind:student="props.item"
            display-context="compact"
            v-on:action="dispatchAction($event, props.item)"
          />
        </td>
      </template>
    </v-data-table>
    
    <v-dialog persistent scrollable v-model="newStudentDialog.show" max-width="500px">
      <StudentsForm
        v-bind:initialData="newStudentDialog.newStudent"
        v-bind:saving="newStudentDialog.saving"
        v-on:cancel="cancelNewStudent"
        v-on:save="saveNewStudent"
      />
    </v-dialog>
  </div>
</template>

<script>
import EntitySearch from "../EntitySearch";
import StudentsForm from "./StudentsForm";
import StudentsAdminActions from "./actions/StudentsAdminActions";

export default {
  components: { 
    "entity-search": EntitySearch,
    StudentsForm,
    StudentsAdminActions
  },
  name: "CourseOfferingStudents",
  data() {
    return {
      selectedValue: null,
      search: "",
      students: [],
      people: [],

      newStudentDialog: {
        show: false,
        newStudent: {},
        saving: false
      }
      
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
    activateNewStudentDialog(newStudent = {}) {
      this.newStudentDialog.show = true;
      this.newStudentDialog.newStudent = newStudent;
    },
    editStudentDialog(newStudent) {
      this.activateNewStudentDialog({ ...newStudent }, true);
    },
    cancelNewStudent() {
      this.newStudentDialog.show = false;
    },
    newStudent() {
      this.activateNewStudentDialog();
    },
    saveNewStudent(newStudent) {
      this.newStudentDialog.saving = true;
      
      const personObject = newStudent;
      newStudent = {};

      newStudent.confirmed = true;
      newStudent.offeringId = this.offeringId;
      newStudent.studentId = personObject.id;
      newStudent.active = true;
        
      this.$http
        .post(`/api/v1/courses/course_offerings/${newStudent.studentId}`, newStudent)
        .then(resp => {
          console.log("ADDED", resp);
          this.students.push(resp.data);
          this.people.push(personObject);
          
          // this.snackbar.text = this.$t("courses.added");
          // this.snackbar.show = true;
        })
        .catch(err => {
           console.error("FAILURE", err.response);
           this.snackbar.text = this.$t("courses.add-failed");
           this.snackbar.show = true;
        })
        .finally(() => {
          this.newStudentDialog.show = false;
          this.newStudentDialog.saving = false;
        });
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
