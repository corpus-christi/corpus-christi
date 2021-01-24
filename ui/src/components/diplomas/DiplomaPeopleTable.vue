<template>
  <div>
    <!-- Header -->
    <v-toolbar class="pa-1" extension-height="64px">
      <!-- These buttons/select controls will help manually edit data.
      <v-layout justify-space-between>
        <v-flex shrink align-self-center>
          <v-toolbar-title>{{ $t("courses.course-offering") }}</v-toolbar-title>
        </v-flex>
        <v-spacer />
        <v-flex shrink justify-self-end>
          <v-btn color="primary" raised v-on:click.stop="newCourseOffering">
            <v-icon left>library_add</v-icon>
            {{ $t("courses.new-offering") }}
          </v-btn>
        </v-flex>
      </v-layout>
      -->
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
      <!--
      </v-layout>
      -->
    </v-toolbar>

    <!-- Table of existing course offerings -->
    <v-data-table
      :headers="headers"
      :search="search"
      :items="showStudents"
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
    <!-- Edit functionality copied from ui/src/components/courses/CourseOfferingsTable.vue.
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
    -->

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

export default {
  name: "DiplomaPeopleTable",
  components: {},
  props: {
    diploma: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      courseOfferingDialog: {
        show: false,
        editMode: false,
        courseOffering: {},
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

      students: [],

      selected: [],
      search: "",
      viewStatus: "active",
    };
  },
  computed: {
    // Put here so that the headers are reactive.
    headers() {
      return [
        /* TODO:
          The data is called in from the file DiplomaDetails.vue in the function loadCourses().
          The data eventually gets stored in this.diploma.studentList.
          However, this data doesn't ask for the variables "firstName," "lastName," "email" or "phone."
          This is an api problem that I don't know how to fix. For now, I've used variables that it DOES call for ("active" & "id").
        */
        {
          text: this.$t("person.name.first"),
          value: "active", //replace "active" with "firstName"
          width: "20%",
        },
        { text: this.$t("person.name.last"), value: "id", width: "20%" }, //replace "id" with "lastName"
        {
          text: this.$t("person.email"),
          value: "email",
          width: "20%",
          //class: "hidden-sm-and-down",
        },
        { text: this.$t("person.phone"), value: "phone", width: "20%" },
        { text: this.$t("actions.header"), width: "20%", sortable: false },
      ];
    },

    options() {
      return [
        { text: this.$t("actions.view-active"), value: "active" },
        { text: this.$t("actions.view-archived"), value: "archived" },
        { text: this.$t("actions.view-all"), value: "all" },
      ];
    },
    showStudents() {
      return this.students;
    },
  },

  mounted() {
    console.log("The Persons table here displays incorrect data. For details, see ui/src/components/diplomas/DiplomaPeopleTable.vue");
    this.students = this.diploma.studentList;
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
          (c) => c.id === courseOffering.id
        );
        Object.assign(this.courseOfferings[idx], courseOffering);
        this.snackbar.text = this.$t("courses.updated");
      } else {
        this.courseOfferings.push(courseOffering);
        this.snackbar.text = this.$t("courses.added");
      }
      
      this.snackbar.show = true;

      this.courseOfferingDialog.show = false;
    }, //*/
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
