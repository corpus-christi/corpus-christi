<template>
  <div>
    <!-- Header -->
    <v-toolbar>
      <v-layout align-center justify-space-between fill-height>
        <v-flex md2>
          <v-toolbar-title>{{ $t("courses.course") }}</v-toolbar-title>
        </v-flex>
        <v-spacer></v-spacer>
        <v-flex md3>
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="$t('actions.search')"
            single-line
            box
            hide-details
            data-cy="courses-table-search"
          ></v-text-field>
        </v-flex>
        <v-spacer></v-spacer>

        <v-flex md3>
          <v-select
            v-model="viewStatus"
            :items="options"
            solo
            hide-details
            data-cy="courses-table-viewstatus"
          ></v-select>
        </v-flex>

        <v-flex shrink justify-self-end>
          <v-btn
            color="primary"
            raised
            v-on:click.stop="newCourse"
            data-cy="courses-table-new"
          >
            <v-icon left>library_add</v-icon>
            {{ $t("courses.new") }}
          </v-btn>
        </v-flex>
      </v-layout>
    </v-toolbar>

    <!-- Table of existing people -->
    <v-data-table
      :headers="headers"
      :search="search"
      :items="showCourses"
      :loading="!tableLoaded"
      class="elevation-1"
      data-cy="courses-table"
    >
      <v-progress-linear
        slot="progress"
        color="primary"
        indeterminate
      ></v-progress-linear>
      <template slot="items" slot-scope="props">
        <td class="hover-hand" @click="clickThrough(props.item)">
          {{ props.item.name }}
        </td>
        <td class="hover-hand" @click="clickThrough(props.item)">
          {{ props.item.description }}
        </td>
        <td>
          <CourseAdminActions
            v-bind:course="props.item"
            display-context="compact"
            v-on:action="dispatchAction($event, props.item)"
          />
        </td>
      </template>
    </v-data-table>

    <v-snackbar v-model="snackbar.show" data-cy="courses-table-snackbar">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false">{{
        $t("actions.close")
      }}</v-btn>
    </v-snackbar>

    <!-- New/Edit dialog -->
    <v-dialog
      v-model="courseDialog.show"
      max-width="500px"
      persistent
      data-cy="courses-table-editor"
    >
      <CourseEditor
        v-bind:editMode="courseDialog.editMode"
        v-bind:initialData="courseDialog.course"
        v-bind:saving="courseDialog.saving"
        v-bind:coursesPool="courses"
        v-on:cancel="cancelCourse"
        v-on:save="saveCourse"
      />
    </v-dialog>

    <!-- Deactivate/archive confirmation -->
    <v-dialog
      v-model="deactivateDialog.show"
      max-width="350px"
      data-cy="courses-table-confirmation"
    >
      <v-card>
        <v-card-text>{{ $t("courses.confirm-archive") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelDeactivate"
            color="secondary"
            flat
            :disabled="deactivateDialog.loading"
          >
            {{ $t("actions.cancel") }}
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deactivate(deactivateDialog.course)"
            color="primary"
            raised
            :disabled="deactivateDialog.loading"
            :loading="deactivateDialog.loading"
          >
            {{ $t("actions.confirm") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import CourseEditor from "./CourseEditor";
import CourseAdminActions from "./actions/CourseAdminActions";

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

      deactivateDialog: {
        show: false,
        course: {},
        loading: false
      },

      snackbar: {
        show: false,
        text: ""
      },

      courses: [],

      tableLoaded: false,
      selected: [],
      search: "",
      viewStatus: "active"
    };
  },
  computed: {
    // Put here so that the headers are reactive.
    headers() {
      return [
        { text: this.$t("courses.title"), value: "name", width: "40%" },
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
        { text: this.$t("actions.view-active"), value: "active" },
        { text: this.$t("actions.view-archived"), value: "archived" },
        { text: this.$t("actions.view-all"), value: "all" }
      ];
    },
    showCourses() {
      switch (this.viewStatus) {
        case "active":
          return this.courses.filter(course => course.active);
        case "archived":
          return this.courses.filter(course => !course.active);
        case "all":
        default:
          return this.courses;
      }
    }
  },

  methods: {
    clickThrough(course) {
      this.$router.push({ name: 'course-details', params: { courseId: course.id }})
    },

    dispatchAction(actionName, course) {
      switch (actionName) {
        case "edit":
          this.editCourse(course);
          break;
        case "deactivate":
          this.confirmDeactivate(course);
          break;
        case "activate":
          this.activate(course);
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

    confirmDeactivate(course) {
      this.deactivateDialog.show = true;
      this.deactivateDialog.course = course;
    },

    cancelDeactivate() {
      this.deactivateDialog.show = false;
    },

    deactivate(course) {
      this.deactivateDialog.loading = true;
      this.$http
        .patch(`/api/v1/courses/courses/${course.id}`, { active: false })
        .then(resp => {
          console.log("EDITED", resp);
          Object.assign(course, resp.data);
          this.snackbar.text = this.$t("courses.archived");
          this.snackbar.show = true;
        })
        .catch(() => {
          this.snackbar.text = this.$t("courses.update-failed");
          this.snackbar.show = true;
        })
        .finally(() => {
          this.deactivateDialog.loading = false;
          this.deactivateDialog.show = false;
        });
    },

    activate(course) {
      this.$http
        .patch(`/api/v1/courses/courses/${course.id}`, { active: true })
        .then(resp => {
          console.log("EDITED", resp);
          Object.assign(course, resp.data);
          this.snackbar.text = this.$t("courses.reactivated");
          this.snackbar.show = true;
        })
        .catch(() => {
          this.snackbar.text = this.$t("courses.update-failed");
          this.snackbar.show = true;
        });
    },

    saveCourse(course) {
      this.courseDialog.saving = true;

      // Hang onto the prereqs of the course
      const prerequisites = course.prerequisites || [];
      // Get rid of the prereqs; not for consumption by the endpoint
      delete course.prerequisites;

      if (this.courseDialog.editMode) {
        // Hang on to the ID of the course being updated.
        const course_id = course.id;
        // Locate the course we're updating in the table.
        const idx = this.courses.findIndex(c => c.id === course.id);
        // Get rid of the ID; not for consumption by endpoint.
        delete course.id;

        let promises = [];
        promises.push(
          this.$http
            .patch(`/api/v1/courses/courses/${course_id}`, course)
            .then(resp => {
              console.log("EDITED", resp);
              Object.assign(this.courses[idx], course);
            })
        );
        promises.push(
          this.$http.patch(
            `/api/v1/courses/courses/prerequisites/${course_id}`,
            { prerequisites: prerequisites.map(prereq => prereq.id) }
          ) // API expects array of IDs
        );

        Promise.all(promises)
          .then(() => {
            this.courses[idx].prerequisites = prerequisites;
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
        // All new courses are active
        course.active = true;
        this.$http
          .post("/api/v1/courses/courses", course)
          .then(resp => {
            console.log("ADDED", resp);
            let newCourse = resp.data;
            newCourse.prerequisites = prerequisites; // Re-attach prereqs so they show up in UI
            this.courses.push(newCourse);

            // Now that course created, add prerequisites to it
            return this.$http.patch(
              `/api/v1/courses/courses/prerequisites/${newCourse.id}`,
              { prerequisites: prerequisites.map(prereq => prereq.id) }
            ); // API expects array of IDs
          })
          .then(resp => {
            console.log("PREREQS", resp);
            this.snackbar.text = this.$t("courses.added");
            this.snackbar.show = true;
          })
          .catch(err => {
            console.error("FAILURE", err);
            this.snackbar.text = this.$t("courses.add-failed");
            this.snackbar.show = true;
          })
          .finally(() => {
            this.courseDialog.show = false;
            this.courseDialog.saving = false;
          });
      }
    }
  },

  mounted: function() {
    this.$http.get("/api/v1/courses/courses").then(resp => {
      this.courses = resp.data;
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
