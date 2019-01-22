<template>
  <div>
    <!-- Header -->
    <v-toolbar class="pa-1" extension-height="64px">
      <v-layout justify-space-between>
        <v-flex shrink align-self-center>
          <v-toolbar-title>{{ $t("courses.course-offering") }}</v-toolbar-title>
        </v-flex>
        <v-spacer></v-spacer>
        <v-flex shrink justify-self-end>
          <v-btn color="primary" raised v-on:click.stop="newCourseOffering">
            <v-icon left>library_add</v-icon>
            {{ $t("courses.new-offering") }}
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
        <v-select
          v-model="viewStatus"
          :items="options"
          solo
          hide-details
          class="max-width-250 mr-2"
        >
        </v-select>
      </v-layout>
    </v-toolbar>

    <!-- Table of existing people -->
    <v-data-table
      :headers="headers"
      :search="search"
      :items="showCourseOfferings"
      class="elevation-1"
      :rows-per-page-items="rowsPerPageItem"
      :pagination.sync="paginationInfo"
    >
      <v-progress-linear
        slot="progress"
        color="primary"
        indeterminate
      ></v-progress-linear>
      <template slot="items" slot-scope="props">
        <td class="hover-hand" @click="clickThrough(props.item)">
          {{ props.item.description }}
        </td>
        <td class="hover-hand" @click="clickThrough(props.item)">
          {{ props.item.maxSize }}
        </td>
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
      <v-btn flat @click="snackbar.show = false">
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>

    <!-- New/Edit dialog -->
    <v-dialog
      persistent
      scrollable
      v-model="courseOfferingDialog.show"
      max-width="500px"
    >
      <CourseOfferingForm
        v-bind:editMode="courseOfferingDialog.editMode"
        v-bind:initialData="courseOfferingDialog.courseOffering"
        v-bind:course="course"
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
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
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
import CourseOfferingForm from "./CourseOfferingForm";
import CourseOfferingAdminActions from "./actions/CourseOfferingAdminActions";

export default {
  name: "CourseOfferingsTable",
  components: {
    CourseOfferingForm,
    CourseOfferingAdminActions
  },
  props: {
    course: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      courseOfferingDialog: {
        show: false,
        editMode: false,
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

      courseOfferings: [],

      selected: [],
      search: "",
      viewStatus: "active"
    };
  },
  computed: {
    // Put here so that the headers are reactive.
    headers() {
      return [
        {
          text: this.$t("courses.description"),
          value: "description",
          width: "80%"
        },
        {
          text: this.$t("courses.max-size"),
          value: "maxSize",
          width: "20%"
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
          return this.courseOfferings.filter(
            courseOffering => courseOffering.active
          );
        case "archived":
          return this.courseOfferings.filter(
            courseOffering => !courseOffering.active
          );
        case "all":
        default:
          return this.courseOfferings;
      }
    }
  },

  mounted() {
    this.courseOfferings = this.course.course_offerings;
  },

  methods: {
    clickThrough(courseOffering) {
      this.$router.push({
        name: "course-offering-details",
        params: { offeringId: courseOffering.id }
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
        .patch(`/api/v1/courses/course_offerings/${courseOffering.id}`, {
          active: false
        })
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
        .patch(`/api/v1/courses/course_offerings/${courseOffering.id}`, {
          active: true
        })
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
      if (courseOffering instanceof Error) {
        this.snackbar.text = this.courseOfferingDialog.editMode
          ? this.$t("courses.update-failed")
          : this.$t("courses.add-failed");
        this.snackbar.show = true;

        this.courseOfferingDialog.show = false;

        return;
      }

      if (this.courseOfferingDialog.editMode) {
        // Locate the record we're updating in the table.
        const idx = this.courseOfferings.findIndex(
          c => c.id === courseOffering.id
        );
        Object.assign(this.courseOfferings[idx], courseOffering);
        this.snackbar.text = this.$t("courses.updated");
      } else {
        this.courseOfferings.push(courseOffering);
        this.snackbar.text = this.$t("courses.added");
      }

      this.snackbar.show = true;

      this.courseOfferingDialog.show = false;
    }
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
