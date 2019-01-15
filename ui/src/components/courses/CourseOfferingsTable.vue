<template>
  <div>
    <!-- Header -->
    <v-toolbar>
      <v-layout align-center justify-space-between fill-height>
        <v-flex md2>
          <v-toolbar-title>{{ $t("courses.course-offering") }}</v-toolbar-title>
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
          ></v-text-field>          
        </v-flex>
        <v-spacer></v-spacer>

        <v-flex md3>
          <v-select v-model="viewStatus" :items="options" solo hide-details></v-select>
        </v-flex>

        <v-flex shrink justify-self-end>
        <v-btn color="primary" raised v-on:click.stop="newCourseOffering">
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
      :items="showCourseOfferings"
      :loading="!tableLoaded"
      class="elevation-1"
    >
      <v-progress-linear slot="progress" color="primary" indeterminate></v-progress-linear>
      <template slot="items" slot-scope="props">
        <td>{{ props.item.course.name }}</td>
        <td>{{ props.item.description }}</td>
        <td>
          <CourseOfferingAdminActions
            v-bind:courseOffering="props.item"
            display-context="compact"
            v-on:action="dispatchAction($event, props.item)"
          />
        </td>
      </template>
    </v-data-table>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false">{{ $t("actions.close") }}</v-btn>
    </v-snackbar>

    <!-- New/Edit dialog -->
    <v-dialog persistant scrollable v-model="courseOfferingDialog.show" max-width="500px">
      <CourseOfferingForm
        v-bind:editMode="courseOfferingDialog.editMode"
        v-bind:initialData="courseOfferingDialog.courseOffering"
        v-bind:saving="courseOfferingDialog.saving"
        v-on:cancel="cancelCourseOffering"
        v-on:save="saveCourseOffering"
      />
    </v-dialog>

    <!-- Deactivate/archive confirmation -->
    <v-dialog v-model="deactivateDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{ $t("courses.confirm-archive") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelDeactivate"
            color="secondary"
            flat
            :disabled="deactivateDialog.loading"
            data-cy
          >{{ $t("actions.cancel") }}</v-btn>
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deactivate(deactivateDialog.courseOffering)"
            color="primary"
            raised
            :disabled="deactivateDialog.loading"
            :loading="deactivateDialog.loading"
            data-cy
          >{{ $t("actions.confirm") }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import CourseOfferingForm from "./CourseOfferingForm";
import CourseOfferingAdminActions from "./actions/CourseOfferingAdminActions";

export default {
  name: "CourseOfferingsTable",
  components: {
    CourseOfferingForm,
    CourseOfferingAdminActions,
  },
  data() {
    return {
      courseOfferingDialog: {
        show: false,
        editMode: false,
        saving: false,
        courseOffering: {}
      },

      deactivateDialog: {
        show: false,
        courseOffering: {},
        loading: false
      },

      snackbar: {
        show: false,
        text: ""
      },

      courseOfferings: [],
      
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
    showCourseOfferings() {
      switch (this.viewStatus) {
        case "active":
          return this.courseOfferings.filter(courseOffering => courseOffering.active);
        case "archived":
          return this.courseOfferings.filter(courseOffering => !courseOffering.active);
        case "all":
          return this.courseOfferings;
        default:
          break;
      }
    }
  },

  methods: {
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

    activateCourseOfferingDialog(courseOffering = {}, editMode = false) {
      this.courseOfferingDialog.editMode = editMode;
      this.courseOfferingDialog.courseOffering = courseOffering;
      this.courseOfferingDialog.show = true;
    },

    editCourseOffering(courseOffering) {
      this.activateCourseOfferingDialog({ ...courseOffering }, true);
    },

    newCourseOffering() {
      this.activateCourseOfferingDialog();
    },

    cancelCourseOffering() {
      this.courseOfferingDialog.show = false;
    },

    confirmDeactivate(courseOffering) {
      this.deactivateDialog.show = true;
      this.deactivateDialog.courseOffering = courseOffering;
    },

    cancelDeactivate() {
      this.deactivateDialog.show = false;
    },

    deactivate(courseOffering) {
      this.deactivateDialog.loading = true;
      this.$http
        .patch(`/api/v1/courses/course_offerings/${courseOffering.id}`, { active: false })
        .then(resp => {
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
        .patch(`/api/v1/courses/course_offerings/${courseOffering.id}`, { active: true })
        .then(resp => {
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

    saveCourseOffering(courseOffering) {
      this.courseOfferingDialog.saving = true;
      if (this.courseOfferingDialog.editMode) {
        // Hang on to the ID of the person being updated.
        const courseOffering_id = courseOffering.id;

        // Locate the person we're updating in the table.
        const idx = this.courseOfferings.findIndex(c => c.id === courseOffering.id);
        // Get rid of the ID; not for consumption by endpoint.
        delete courseOffering.id;

        this.$http
          .patch(`/api/v1/courses/course_offerings/${courseOffering_id}`, courseOffering)
          .then(resp => {
            console.log("EDITED", resp);
            Object.assign(this.courseOfferings[idx], courseOffering);
            this.snackbar.text = this.$t("courses.updated");
            this.snackbar.show = true;
          })
          .catch(err => {
            console.error("FALURE", err.response);
            this.snackbar.text = this.$t("courses.update-failed");
            this.snackbar.show = true;
          })
          .finally(() => {
            this.courseOfferingDialog.show = false;
            this.courseOfferingDialog.saving = false;
          });
      } else {
        this.$http
          .post("/api/v1/courses/course_offerings", courseOffering)
          .then(resp => {
            console.log("ADDED", resp);
            this.courseOfferings.push(resp.data);
            this.snackbar.text = this.$t("courses.added");
            this.snackbar.show = true;
          })
          .catch(err => {
            console.error("FAILURE", err.response);
            this.snackbar.text = this.$t("courses.add-failed");
            this.snackbar.show = true;
          })
          .finally(() => {
            this.courseOfferingDialog.show = false;
            this.courseOfferingDialog.saving = false;
          });
      }

      this.courseOfferingDialog.show = false;
    }
  },

  mounted: function() {
    this.$http.get("/api/v1/courses/course_offerings").then(resp => {
      this.courseOfferings = resp.data;
      this.tableLoaded = true;             
    });
  }
};
</script>
