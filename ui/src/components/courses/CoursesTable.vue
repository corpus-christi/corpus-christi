<template>
  <div>
    <!-- Header -->
    <v-toolbar>
      <v-toolbar-title> {{ $t("courses.course") }}</v-toolbar-title>
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
        small
        fab
        color="primary"
        absolute
        dark
        bottom
        right
        v-on:click.stop="newCourse"
      >
        <v-icon>add</v-icon>
      </v-btn>
    </v-toolbar>

    <!-- Table of existing people -->
    <v-data-table
      :headers="headers"
      :items="courses"
      :search="search"
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td>{{ props.item.title }}</td>
        <td>{{ props.item.description }}</td>
        <td>{{ props.item.enrolled }}</td>
        <td>
          <CourseAdminActions
            v-bind:course="props.item"
            display-context="compact"
            v-on:action="dispatchAction($event, props.item)"/>
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
    <v-dialog v-model="courseDialog.show" max-width="500px">
      <CourseForm
        v-bind:editMode="courseDialog.editMode"
        v-bind:initialData="courseDialog.course"
        v-on:cancel="cancelCourse"
        v-on:save="saveCourse"
      />
    </v-dialog>
  </div>
</template>

<script>
import CourseForm from "./CourseForm";
import CourseAdminActions from "./CourseAdminActions";

export default {
  name: "CoursesTable",
  components: {
    CourseForm,
    CourseAdminActions
  },
  data() {
    return {
      courseDialog: {
        show: false,
        editMode: false,
        course: {}
      },

      snackbar: {
        show: false,
        text: ""
      },

      selected: [],
      courses: [],
      search: "",
    };
  },
  computed: {
    // Put here so that the headers are reactive.
    headers() {
      return [
        { text: this.$t("courses.title"), value: "title", width: "20%" },
        { text: this.$t("courses.description"), value: "description", width: "20%" },
        { text: this.$t("courses.enrolled"), value: "enrolled", width: "15%" }
      ];
    }
  },
  methods: {
    dispatchAction(actionName, course) {
      switch(actionName) {
        case "edit":
          this.editCourse(course);
          break;
        case "deactivate":
          // todo: deactivate course
          break;
        default:
          break;
      }
    },

    activateCourseDialog(course = {}, editMode = false) {
      this.courseDialog.editMode = editMode;
      this.courseDialog.course = course;
      this.courseDialog.show = true;
    },

    editCourse(course) {
      this.activateCourseDialog({ ...course }, true);
    },

    newCourse() {
      this.activateCourseDialog();
    },

    cancelCourse() {
      this.courseDialog.show = false;
    },

    saveCourse(course) {
      if (this.courseDialog.editMode) {
        // Hang on to the ID of the person being updated.
        const course_id = course.id;
        // Locate the person we're updating in the table.
        const idx = this.courses.findIndex(c => c.id === course.id);
        // Get rid of the ID; not for consumption by endpoint.
        delete course.id;

      //   this.$http
      //     .put(`/api/v1/people/persons/${person_id}`, person)
      //     .then(resp => {
      //       console.log("EDITED", resp);
      //       Object.assign(this.people[idx], person);
      //     })
      //     .catch(err => console.error("FALURE", err.response));
      // } else {
      //   this.$http
      //     .post("/api/v1/people/persons", person)
      //     .then(resp => {
      //       console.log("ADDED", resp);
      //       this.people.push(resp.data);
      //     })
      //     .catch(err => console.error("FAILURE", err.response));
      }
      this.courseDialog.show = false;
    }
  },

  mounted: function() {
    // this.$http
    //   .get("/api/v1/people/persons")
    //   .then(resp => (this.courses = resp.data));
  }
};
</script>
