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
 
      <v-select 
        :label="$t('actions.view-Archived')"
        v-model="viewStatus"
        :items="options"
        standard
        hide-details>
        </v-select>
    
      <v-btn
        color="primary"
        raised
        v-on:click.stop="newCourse"
      >
        <v-icon left>library_add</v-icon>
        {{ $t("courses.new") }}
      </v-btn>
    </v-toolbar>

    <!-- Table of existing people -->
    <v-data-table
      :headers="headers"
      :search="search"
      :items="showCourses"
      :loading="!tableLoaded"
      class="elevation-1"
    >
      <v-progress-linear
        slot="progress"
        color="blue"
        indeterminate
      ></v-progress-linear>
      <template slot="items" slot-scope="props">
        <td>{{ props.item.title }}</td>
        <td>{{ props.item.description }}</td>
        <td>
          <CourseAdminActions
            v-bind:course="props.item"
            display-context="compact"
            v-on:action="dispatchAction($event, props.item)"
          />
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
      <CourseEditor
        v-bind:editMode="courseDialog.editMode"
        v-bind:initialData="courseDialog.course"
        v-bind:saving="courseDialog.saving"
        v-on:cancel="cancelCourse"
        v-on:save="saveCourse"
      />
    </v-dialog>
  </div>
</template>

<script>
import CourseEditor from "./CourseEditor";
import CourseAdminActions from "./CourseAdminActions";

export default {
  name: "CoursesTable",
  components: {
    CourseEditor,
    CourseAdminActions
  },
  data() {
    return {
      courseDialog: {
        show: false,
        editMode: false,
        saving: false,
        course: {}
      },

      snackbar: {
        show: false,
        text: ""
      },

      activeCourses: [],
      archivedCourses: [],
      courses: [],

      tableLoaded: false,
      selected: [],
      search: "",
      viewStatus: "active",
    };
  },
  computed: {
    // Put here so that the headers are reactive.
    headers() {
      return [
        { text: this.$t("courses.title"), value: "title", width: "40%" },
        {
          text: this.$t("courses.description"),
          value: "description",
          width: "60%"
        },
        { text: this.$t("actions.header"), sortable: false }
      ];
    },

    options() {
      return [
        {text: this.$t("actions.view-active"), value: "active"},
        {text: this.$t("actions.view-archived"), value: "archived"},
        {text: this.$t("actions.view-all"), value: "all"}
      ]
    },
    showCourses() {
      // return this.showingArchived ? this.courses : this.courses.filter(course => course.active)
      switch (this.viewStatus) {
        case "active":
          return this.activeCourses;
          break;
        case "archived":
          return this.archivedCourses;
          break;
        case "all":
          return this.courses;
          break;
      }
  
    },

  },

  methods: {
    dispatchAction(actionName, course) {
      switch (actionName) {
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
      this.courseDialog.saving = true;
      if (this.courseDialog.editMode) {
        // Hang on to the ID of the person being updated.
        const course_id = course.id;
        // Locate the person we're updating in the table.
        const idx = this.courses.findIndex(c => c.id === course.id);
        // Get rid of the ID; not for consumption by endpoint.
        delete course.id;

        this.$http
          .put(`/api/v1/courses/courses/${course_id}`, course)
          .then(resp => {
            console.log("EDITED", resp);
            Object.assign(this.courses[idx], course);
            this.snackbar.text = this.$t("courses.updated");
            this.snackbar.show = true;
          })
          .catch(err => {
            console.error("FALURE", err.response);
            this.snackbar.text = this.$t("courses.update-failed");
            this.snackbar.show = true;
          })
          .finally(() => {
            this.courseDialog.show = false;
            this.courseDialog.saving = false;
          });
      } else {
        this.$http
          .post("/api/v1/courses/courses", course)
          .then(resp => {
            console.log("ADDED", resp);
            this.courses.push(resp.data);
            this.snackbar.text = this.$t("courses.added");
            this.snackbar.show = true;
          })
          .catch(err => {
            console.error("FAILURE", err.response);
            this.snackbar.text = this.$t("courses.add-failed");
            this.snackbar.show = true;
          })
          .finally(() => {
            this.courseDialog.show = false;
            this.courseDialog.saving = false;
          });
      }

      this.courseDialog.show = false;

    }
  },

  mounted: function() {
    this.$http
      .get("/api/v1/courses/courses")
      .then(resp => {
        this.courses = resp.data
        this.activeCourses = this.courses.filter(course => course.active)
        this.archivedCourses = this.courses.filter(course => !course.active)
        this.tableLoaded = true;
        console.log(this.activeCourses, this.archivedCourses, this.courses)
      });

  }
};
</script>
