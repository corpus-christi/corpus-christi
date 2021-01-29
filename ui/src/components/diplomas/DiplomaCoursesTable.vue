<template>
  <div>
    <!-- Header -->
    <v-toolbar class="pa-1" extension-height="64px">
      <!-- These buttons/select controls will help manually edit data. -->
      <v-layout justify-space-between>
        <v-flex shrink align-self-center>
          <v-toolbar-title>{{ $t("courses.course") }}</v-toolbar-title>
        </v-flex>
        <v-spacer />
        <v-flex shrink justify-self-end>
          <v-btn color="primary" raised v-on:click.stop="addCourse">
            <v-icon left>library_add</v-icon>
            {{ $t("courses.new") }}
          </v-btn>
        </v-flex>
      </v-layout>
      <v-layout row slot="extension" justify-space-between align-center>
        <v-flex>
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="$t('actions.search')"
            single-line
            hide-details
            class="max-width-250 mr-2"
          ></v-text-field>
        </v-flex>
        <!--
        <v-select
          v-model="viewStatus"
          :items="options"
          solo
          hide-details
          class="max-width-250 mr-2"
        >
        </v-select>
        -->
      </v-layout>
    </v-toolbar>

    <!-- Table of existing course offerings -->
    <v-data-table
      :headers="headers"
      :search="search"
      :items="showCourses"
      class="elevation-1"
      :items-per-page-options="rowsPerPageItem"
      hide-default-footer
      @page-count="pageCount = $event"
      :page.sync="page"
    >
      <v-progress-linear
        slot="progress"
        color="primary"
        indeterminate
      ></v-progress-linear>
      <!-- No idea what this does. Copied over from ui/src/components/courses/CoursesTable.vue.
      <template slot="items" slot-scope="props">
        <td :data-cy="'first-name-' + item.id">
          {{ item.firstName }}
        </td>
        <td :data-cy="'last-name-' + item.id">
          {{ item.lastName }}
        </td>
        <td class="hover-hand" @click="clickThrough(props.item)">
          {{ props.item.description }}
        </td>
        <td class="hover-hand" @click="clickThrough(props.item)">
          {{ props.item.maxSize }}
        </td>
      </template>
      -->
    </v-data-table>
    <div class="text-center pt-2">
      <v-pagination v-model="page" :length="pageCount"></v-pagination>
    </div>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn text @click="snackbar.show = false">
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>

    <!-- New/Edit dialog -->
    <!-- Edit functionality copied from ui/src/components/courses/CourseOfferingsTable.vue. -->
    <v-dialog
      persistent
      scrollable
      v-model="newCourseDialog.show"
      max-width="500px"
    >
      <!---->
      <DiplomaNewCourseForm
        v-bind:editMode="newCourseDialog.editMode"
        v-bind:initialData="newCourseDialog.course"
        v-on:cancel="cancelNewCourse"
        v-on:save="saveNewCourse"
      />
      <!---->
    </v-dialog>

    <!-- Deactivate/archive confirmation -->
    <v-dialog v-model="deactivateDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{ $t("courses.confirm-archive") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelDeactivate"
            color="secondary"
            text
            :disabled="deactivateDialog.loading"
            data-cy
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer />
          <v-btn
            v-on:click="deactivate(deactivateDialog.courseOffering)"
            color="primary"
            raised
            :disabled="deactivateDialog.loading"
            :loading="deactivateDialog.loading"
            data-cy
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import DiplomaNewCourseForm from "./DiplomaNewCourseForm.vue";

export default {
  name: "DiplomaCoursesTable",
  components: {
    DiplomaNewCourseForm,
  },
  props: {
    diploma: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      newCourseDialog: {
        show: false,
        editMode: false,
        course: {},
      },

      deactivateDialog: {
        show: false,
        courseOffering: {},
        loading: false,
      },

      snackbar: {
        show: false,
        text: "",
      },

      rowsPerPageItem: [
        10,
        15,
        25,
        { text: "$vuetify.dataIterator.rowsPerPageAll", value: -1 },
      ],

      page: 1,
      pageCount: 0,

      courses: [],

      selected: [],
      search: "",
      viewStatus: "active",
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
          width: "60%",
        },
        { text: this.$t("actions.header"), sortable: false },
      ];
    },

    options() {
      return [
        { text: this.$t("actions.view-active"), value: "active" },
        { text: this.$t("actions.view-archived"), value: "archived" },
        { text: this.$t("actions.view-all"), value: "all" },
      ];
    },

    showCourses() {
      return this.courses;
    },
  },

  mounted() {
    this.courses = this.diploma.courseList;
  },

  methods: {
    fetchPeopleList() {
      this.tableLoaded = false;
      this.$http
        .get("/api/v1/people/persons?include_images=1")
        .then((resp) => {
          this.peopleList = resp.data;
          this.tableLoaded = true;
        })
        .catch((err) => console.error("FAILURE", err.response));
    },

    /* These Functions are copied over from the ui/src/components/courses/CourseOfferingsTable.vue. They may be useful.
    clickThrough(courseOffering) {
      this.$router.push({
        name: "course-offering-details",
        params: { offeringId: courseOffering.id },
      });
    },

    dispatchAction(actionName, courseOffering) {
      switch (actionName) {
        case "edit":
          this.editCourseOffering(courseOffering);
          break;
        case "deactivate":
          this.confirmDeactivate(courseOffering);
          break;
        case "activate":
          this.activate(courseOffering);
          break;
        default:
          break;
      }
    },
    */
    activateNewCourseDialog(course = {}, editMode = false) {
      this.newCourseDialog.editMode = editMode;
      this.newCourseDialog.course = course;
      this.newCourseDialog.show = true;
    },
    /*
    editCourseOffering(courseOffering) {
      this.activateNewCourseDialog({ ...courseOffering }, true);
    },
    */
    addCourse() {
      this.activateNewCourseDialog();
    },

    cancelNewCourse() {
      this.newCourseDialog.show = false;
    },
    /*
    confirmDeactivate(courseOffering) {
      this.deactivateDialog.show = true;
      this.deactivateDialog.courseOffering = courseOffering;
    },
    //*/
    cancelDeactivate() {
      this.deactivateDialog.show = false;
    },
    /*
    deactivate(courseOffering) {
      this.deactivateDialog.loading = true;
      this.$http
        .patch(`/api/v1/courses/course_offerings/${courseOffering.id}`, {
          active: false,
        })
        .then((resp) => {
          console.log("EDITED", resp);
          Object.assign(courseOffering, resp.data);
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

    activate(courseOffering) {
      this.$http
        .patch(`/api/v1/courses/course_offerings/${courseOffering.id}`, {
          active: true,
        })
        .then((resp) => {
          console.log("EDITED", resp);
          Object.assign(courseOffering, resp.data);
          this.snackbar.text = this.$t("courses.reactivated");
          this.snackbar.show = true;
        })
        .catch(() => {
          this.snackbar.text = this.$t("courses.update-failed");
          this.snackbar.show = true;
        });
    },
    //*/
    saveNewCourse(course) {
      if (course instanceof Error) {
        this.snackbar.text = this.newCourseDialog.editMode
          ? this.$t("courses.update-failed")
          : this.$t("courses.add-failed");
        this.snackbar.show = true;

        this.newCourseDialog.show = false;

        return;
      }
      if (this.newCourseDialog.editMode) {
        // Locate the record we're updating in the table.
        const idx = this.course.findIndex((c) => c.id === course.id);
        Object.assign(this.course[idx], course);
        this.snackbar.text = this.$t("courses.updated");
      } else {
        this.courses.push(course);
        this.snackbar.text = this.$t("courses.added");
      }
      /*
      this.snackbar.show = true;
      */
      this.newCourseDialog.show = false;
    },
  },
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
