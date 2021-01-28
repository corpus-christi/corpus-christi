<template>
  <div>
    <!-- Header -->
    <v-toolbar class="pa-1" extension-height="64px">
      <!-- These buttons/select controls will help manually edit data. -->
      <v-layout justify-space-between>
        <v-flex shrink align-self-center>
          <v-toolbar-title>{{ $t("courses.students") }}</v-toolbar-title>
        </v-flex>
        <v-spacer />
        <v-flex shrink justify-self-end>
          <v-btn color="primary" raised v-on:click.stop="newPerson">
            <v-icon left>library_add</v-icon>
            <!-- TODO: Create a Localization entry for "ADD A NEW STUDENT" -->
            {{ $t("courses.create-new-person") }}
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
    <!-- Edit functionality copied from ui/src/components/courses/CourseOfferingsTable.vue. -->
    <v-dialog
      persistent
      scrollable
      v-model="newPersonDialog.show"
      max-width="500px"
    >
      <DiplomaNewPersonForm
        v-bind:editMode="newPersonDialog.editMode"
        v-bind:initialData="newPersonDialog.person"
        v-on:cancel="cancelNewPerson"
        v-on:save="saveNewPerson"
      />
    </v-dialog>
    <!---->

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
            v-on:click="deactivate(deactivateDialog.person)"
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
import DiplomaNewPersonForm from "./DiplomaNewPersonForm.vue";

export default {
  name: "DiplomaPersonTable",
  components: {
    DiplomaNewPersonForm,
  },
  props: {
    diploma: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      newPersonDialog: {
        show: false,
        editMode: false,
        person: {},
      },

      deactivateDialog: {
        show: false,
        person: {},
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
    console.log(
      "The Persons table here displays incorrect data. For details, see ui/src/components/diplomas/DiplomaPeopleTable.vue"
    );
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
    clickThrough(person) {
      this.$router.push({
        name: "course-offering-details",
        params: { offeringId: person.id },
      });
    },

    dispatchAction(actionName, person) {
      switch (actionName) {
        case "edit":
          this.editPerson(person);
          break;
        case "deactivate":
          this.confirmDeactivate(person);
          break;
        case "activate":
          this.activate(person);
          break;
        default:
          break;
      }
    },
    */
    activateNewPersonDialog(person = {}, editMode = false) {
      this.newPersonDialog.editMode = editMode;
      this.newPersonDialog.person = person;
      this.newPersonDialog.show = true;
    },
    /*
    editPerson(person) {
      this.activateNewPersonDialog({ ...person }, true);
    },
    //*/
    newPerson() {
      this.activateNewPersonDialog();
    },
    //*/
    cancelNewPerson() {
      this.newPersonDialog.show = false;
    },
    /*
    confirmDeactivate(person) {
      this.deactivateDialog.show = true;
      this.deactivateDialog.person = person;
    },
    //*/
    cancelDeactivate() {
      this.deactivateDialog.show = false;
    },
    /*
    deactivate(person) {
      this.deactivateDialog.loading = true;
      this.$http
        .patch(`/api/v1/courses/course_offerings/${person.id}`, {
          active: false,
        })
        .then((resp) => {
          console.log("EDITED", resp);
          Object.assign(person, resp.data);
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

    activate(person) {
      this.$http
        .patch(`/api/v1/courses/course_offerings/${person.id}`, {
          active: true,
        })
        .then((resp) => {
          console.log("EDITED", resp);
          Object.assign(person, resp.data);
          this.snackbar.text = this.$t("courses.reactivated");
          this.snackbar.show = true;
        })
        .catch(() => {
          this.snackbar.text = this.$t("courses.update-failed");
          this.snackbar.show = true;
        });
    },
    //*/
    saveNewPerson(person) {
      if (person instanceof Error) {
        this.snackbar.text = this.newPersonDialog.editMode
          ? this.$t("courses.update-failed")
          : this.$t("courses.add-failed");
        this.snackbar.show = true;

        this.newPersonDialog.show = false;

        return;
      }

      if (this.newPersonDialog.editMode) {
        // Locate the record we're updating in the table.
        const idx = this.students.findIndex(
          (c) => c.id === person.id
        );
        Object.assign(this.students[idx], person);
        this.snackbar.text = this.$t("courses.updated");
      } else {
        this.students.push(person);
        this.snackbar.text = this.$t("courses.added");
      }
      
      this.snackbar.show = true;

      this.newPersonDialog.show = false;
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
