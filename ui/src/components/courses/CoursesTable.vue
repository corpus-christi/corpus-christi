<template>
  <div>
    <!-- Header -->
    <v-toolbar class="pa-1" extension-height="64px">
      <v-layout justify-space-between>
        <v-flex shrink align-self-center>
          <v-toolbar-title>{{ $t("courses.course") }}</v-toolbar-title>
        </v-flex>
        <v-spacer></v-spacer>
        <v-flex shrink justify-self-end>
          <v-btn
            color="primary"
            raised
            v-on:click.stop="newCourse"
            data-cy="courses-table-new"
            class="hidden-xs-only mr-2"
          >
            <v-icon left>library_add</v-icon>
            <span class="mr-1"> {{ $t("courses.new") }} </span>
          </v-btn>
          <v-btn
            class="hidden-sm-and-up"
            color="primary"
            raised
            fab
            v-on:click.stop="newCourse"
            data-cy="add-courseOffering-small"
          >
            <v-icon dark>add</v-icon>
          </v-btn>
        </v-flex>
      </v-layout>

      <v-layout row slot="extension" justify-space-between align-center>
        <v-text-field
          v-model="search"
          append-icon="search"
          v-bind:label="$t('actions.search')"
          single-line
          hide-details
          data-cy="courses-table-search"
          class="max-width-250 mr-2"
        ></v-text-field>

        <v-select
          v-model="viewStatus"
          :items="options"
          solo
          hide-details
          data-cy="courses-table-viewstatus"
          class="max-width-250 mr-2"
        ></v-select>
      </v-layout>
    </v-toolbar>

    <!-- Table of existing people -->
    <v-data-table
      :headers="headers"
      :search="search"
      :items="showCourses"
      :loading="!tableLoaded"
      :rows-per-page-items="rowsPerPageItem"
      :pagination.sync="paginationInfo"
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
      scrollable
      data-cy="courses-table-editor"
    >
      <CourseForm
        v-bind:editMode="courseDialog.editMode"
        v-bind:initialData="courseDialog.course"
        v-bind:courses="courses"
        v-on:cancel="cancelCourse"
        v-on:save="save"
        v-on:addAnother="addAnother"
        v-bind:saveLoading="courseDialog.saveLoading"
        v-bind:addMoreLoading="courseDialog.addMoreLoading"
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
import CourseForm from "./CourseForm";
import CourseAdminActions from "./actions/CourseAdminActions";

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
        course: {},
        saveLoading: false,
        addMoreLoading: false
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

      rowsPerPageItem: [
        10,
        15,
        25,
        { text: "$vuetify.dataIterator.rowsPerPageAll", value: -1 }
      ],

      paginationInfo: {
        sortBy: "start",
        rowsPerPage: 10,
        page: 1
      },

      courses: [],

      tableLoaded: false,
      addMore: false,
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
      this.$router.push({
        name: "course-details",
        params: { courseId: course.id }
      });
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
          this.showSnackbar(this.$t("courses.archived"));
          this.snackbar.show = true;
        })
        .catch(() => {
          this.showSnackbar(this.$t("courses.update-failed"));
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
          this.showSnackbar(this.$t("courses.reactivated"));
          this.snackbar.show = true;
        })
        .catch(() => {
          this.showSnackbar(this.$t("courses.update-failed"));
          this.snackbar.show = true;
        });
    },

    clearCourse() {
      this.addMore = false;
      this.courseDialog.saveLoading = false;
      this.courseDialog.addMoreLoading = false;
      this.courseDialog.course = {};
    },

    cancelCourse() {
      this.addMore = false;
      this.courseDialog.show = false;
      this.courseDialog.saveLoading = false;
      this.courseDialog.addMoreLoading = false;
    },

    addAnother(course) {
      this.addMore = true;
      this.courseDialog.addMoreLoading = true;
      this.saveCourse(course);
    },

    save(course) {
      this.courseDialog.saveLoading = true;
      this.saveCourse(course);
    },

    async saveCourse(course) {
      let courseAttrs = {
        description: course.description,
        name: course.name
      };

      let newImageId = course.newImageId;
      let oldImageId = await this.getOldImageId(course.id);

      var prereqMap = {};
      if (course.prerequisites) {
        prereqMap = course.prerequisites.map(prereq => prereq.id);
      }

      if (this.courseDialog.editMode) {
        let promises = [];
        promises.push(
          this.$http
            .patch(`/api/v1/courses/courses/${course.id}`, courseAttrs)
            .then(resp => {
              console.log("EDITED", resp);
              return resp;
            })
        );

        if (newImageId) {
          // an image was added or edited
          if (oldImageId) {
            // an image was edited (PUT)
            promises.push(
              this.$http.put(
                `/api/v1/courses/${
                  course.id
                }/images/${newImageId}?old=${oldImageId}`
              )
            );
          } else {
            // an image was added (POST)
            promises.push(
              this.$http.post(
                `/api/v1/courses/${course.id}/images/${newImageId}`
              )
            );
          }
        } else {
          // no image existed or was deleted
          if (oldImageId) {
            // an image was removed (DELETE)
            promises.push(
              this.$http.delete(
                `/api/v1/courses/${course.id}/images/${oldImageId}`
              )
            );
          } else {
            // an image never existed and never was added (NOTHING)
            // case put in for readability
          }
        }

        promises.push(
          this.$http.patch(
            `/api/v1/courses/courses/${course.id}/prerequisites`,
            { prerequisites: prereqMap } // API expects array of IDs
          )
        );

        Promise.all(promises)
          .then(resps => {
            let newCourse = resps[0].data;
            newCourse.prerequisites = course.prerequisites; // Re-attach prereqs so they show up in UI
            const idx = this.courses.findIndex(c => c.id === course.id);
            Object.assign(this.courses[idx], course);
            this.cancelCourse();
            this.refreshCourseList();
            this.showSnackbar(this.$t("courses.updated"));
          })
          .catch(err => {
            console.error("FALURE", err.response);
            this.courseDialog.saveLoading = false;
            this.showSnackbar(this.$t("courses.update-failed"));
          });
      } else {
        // creating a new course
        // All new courses are active
        courseAttrs.active = true;
        let newCourse;
        this.$http
          .post("/api/v1/courses/courses", courseAttrs)
          .then(resp => {
            console.log("ADDED", resp);
            newCourse = resp.data;
            newCourse.prerequisites = course.prerequisites; // Re-attach prereqs so they show up in UI

            // Now that course created, add prerequisites to it
            return this.$http.patch(
              `/api/v1/courses/courses/${newCourse.id}/prerequisites`,
              { prerequisites: prereqMap } // API expects array of IDs
            );
          })
          .then(resp => {
            console.log("PREREQS", resp);
            return newImageId
              ? this.$http.post(
                  `/api/v1/courses/${newCourse.id}/images/${newImageId}`
                )
              : null;
          })
          .then(resp => {
            console.log("IMAGE ADDED TO COURSE", resp);
            this.courses.push(course);
            this.showSnackbar(this.$t("courses.added"));
            if (this.addMore) {
              this.clearCourse();
            } else {
              this.cancelCourse();
            }
            this.refreshCourseList();
          })
          .catch(err => {
            console.error("FAILURE", err);
            this.courseDialog.saveLoading = false;
            this.courseDialog.addMoreLoading = false;
            this.showSnackbar(this.$t("courses.add-failed"));
          });
      }
    },

    async getOldImageId(id) {
      if (!id) {
        return null;
      }
      return await this.$http
        .get(`/api/v1/courses/courses/${id}?include_images=1`)
        .then(resp => {
          if (resp.data.images && resp.data.images.length > 0) {
            return resp.data.images[0].image_id;
          } else {
            return null;
          }
        })
        .catch(err => {
          console.error("ERROR FETCHING COURSE", err);
          return null;
        });
    },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },

    refreshCourseList() {
      this.$http.get("/api/v1/courses/courses?include_images=1").then(resp => {
        this.courses = resp.data;
        this.tableLoaded = true;
      });
    }
  },

  mounted: function() {
    this.refreshCourseList();
  }
};
</script>

<style scoped>
.hover-hand {
  cursor: pointer;
}

.max-width-250 {
  max-width: 250px;
}
</style>
