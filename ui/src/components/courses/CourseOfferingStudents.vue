<template>
  <div>
    <v-toolbar class="pa-1" extension-height="64px">
      <v-layout justify-space-between>
        <v-flex shrink align-self-center>
          <v-toolbar-title>{{ $t("courses.students") }}</v-toolbar-title>
        </v-flex>
        <v-spacer></v-spacer>

        <v-flex shrink justify-self-end>
          <v-btn
            color="primary"
            raised
            v-on:click.stop="newStudent"
            class="hidden-xs-only mr-2"
          >
            <v-icon dark left>add</v-icon>
            <span class="mr-1"> {{ $t("actions.add-person") }} </span>
          </v-btn>
          <v-btn
            class="hidden-sm-and-up"
            color="primary"
            raised
            fab
            v-on:click.stop="newStudent"
            data-cy="add-student-small"
          >
            <v-icon dark>add</v-icon>
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
    <v-data-table
      :headers="headers"
      :items="showStudents"
      :search="search"
      :loading="loading"
      class="elevation-1"
      :rows-per-page-items="rowsPerPageItem"
      :pagination.sync="paginationInfo"
    >
      <template slot="items" slot-scope="props">
        <td>{{ props.item.person.firstName }}</td>
        <td>{{ props.item.person.lastName }}</td>
        <td>{{ props.item.person.email }}</td>
        <td>{{ props.item.person.phone }}</td>
        <td>
          <StudentsAdminActions
            v-bind:student="props.item"
            display-context="compact"
            v-on:action="dispatchAction($event, props.item)"
          />
        </td>
      </template>
    </v-data-table>

    <v-dialog
      persistent
      scrollable
      v-model="newStudentDialog.show"
      max-width="500px"
    >
      <StudentsForm
        v-bind:initialData="newStudentDialog.newStudent"
        v-bind:saving="newStudentDialog.saving"
        v-on:cancel="cancelNewStudent"
        v-on:save="saveNewStudent"
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
            v-on:click="deactivate(deactivateDialog.student)"
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

    <!-- Confirm Dialog -->
    <v-dialog v-model="confirmDialog.show" max-width="400px">
      <v-card>
        <v-card-text>{{ $t("courses.confirm-student") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelConfirmDialog"
            color="secondary"
            flat
            :disabled="confirmDialog.confirming"
            data-cy
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="rejectStudent(confirmDialog.student)"
            color="accent"
            raised
            :loading="confirmDialog.confirming"
            data-cy
            >{{ $t("courses.reject") }}</v-btn
          >
          <v-btn
            v-on:click="confirmStudent(confirmDialog.student)"
            color="primary"
            raised
            :disabled="confirmDialog.confirming"
            :loading="confirmDialog.confirming"
            data-cy
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import StudentsForm from "./StudentsForm";
import StudentsAdminActions from "./actions/StudentsAdminActions";

export default {
  components: {
    StudentsForm,
    StudentsAdminActions
  },
  name: "CourseOfferingStudents",
  data() {
    return {
      selectedValue: null,
      search: "",
      students: [],
      viewStatus: "active",
      loading: false,

      newStudentDialog: {
        show: false,
        newStudent: {},
        saving: false
      },

      deactivateDialog: {
        show: false,
        student: {},
        loading: false
      },

      confirmDialog: {
        show: false,
        student: {},
        confirming: false
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
      }
    };
  },

  props: {
    offeringId: null
  },

  computed: {
    headers() {
      return [
        {
          text: this.$t("person.name.first"),
          value: "person.firstName",
          width: "20%"
        },
        {
          text: this.$t("person.name.last"),
          value: "person.lastName",
          width: "20%"
        },
        {
          text: this.$t("person.email"),
          value: "person.email",
          width: "22.5%"
        },
        {
          text: this.$t("person.phone"),
          value: "person.phone",
          width: "22.5%"
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

    showStudents() {
      switch (this.viewStatus) {
        case "active":
          return this.students.filter(student => student.active);
        case "archived":
          return this.students.filter(student => !student.active);
        case "all":
        default:
          return this.students;
      }
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
        .post(
          `/api/v1/courses/course_offerings/${newStudent.studentId}`,
          newStudent
        )
        .then(resp => {
          console.log("ADDED", resp);
          this.students.push(resp.data);

          this.snackbar.text = this.$t("courses.added");
          this.snackbar.show = true;
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
    },

    dispatchAction(actionName, student) {
      switch (actionName) {
        case "deactivate":
          this.confirmDeactivate(student);
          break;
        case "activate":
          this.activate(student);
          break;
        case "confirm":
          this.showConfirmDialog(student);
          break;
        default:
          break;
      }
    },

    showConfirmDialog(student) {
      this.confirmDialog.show = true;
      this.confirmDialog.student = student;
    },

    rejectStudent(student) {
      this.confirmDialog.confirming = true;
      this.$http
        .patch(`/api/v1/courses/students/${student.id}`, { active: false })
        .then(resp => {
          console.log("EDITED", resp);
          Object.assign(student, resp.data);
          this.snackbar.text = this.$t("courses.archived");
          this.snackbar.show = true;
        })
        .catch(() => {
          this.snackbar.text = this.$t("courses.update-failed");
          this.snackbar.show = true;
        })
        .finally(() => {
          this.confirmDialog.confirming = false;
          this.confirmDialog.show = false;
        });
    },

    confirmStudent(student) {
      this.$http
        .patch(`/api/v1/courses/students/${student.id}`, { confirmed: true })
        .then(resp => {
          console.log("EDITED", resp);
          Object.assign(student, resp.data);
          this.snackbar.text = this.$t("courses.reactivated");
          this.snackbar.show = true;
        })
        .catch(() => {
          this.snackbar.text = this.$t("courses.update-failed");
          this.snackbar.show = true;
        })
        .finally(() => {
          this.confirmDialog.show = false;
          this.confirmDialog.confirming = false;
        });
    },

    cancelConfirmDialog() {
      this.confirmDialog.show = false;
    },

    confirmDeactivate(student) {
      this.deactivateDialog.show = true;
      this.deactivateDialog.student = student;
    },

    cancelDeactivate() {
      this.deactivateDialog.show = false;
    },

    deactivate(student) {
      this.deactivateDialog.loading = true;
      this.$http
        .patch(`/api/v1/courses/students/${student.id}`, { active: false })
        .then(resp => {
          console.log("EDITED", resp);
          Object.assign(student, resp.data);
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

    activate(student) {
      this.$http
        .patch(`/api/v1/courses/students/${student.id}`, { active: true })
        .then(resp => {
          console.log("EDITED", resp);
          Object.assign(student, resp.data);
          this.snackbar.text = this.$t("courses.reactivated");
          this.snackbar.show = true;
        })
        .catch(() => {
          this.snackbar.text = this.$t("courses.update-failed");
          this.snackbar.show = true;
        });
    }
  },

  mounted: function() {
    const id = this.offeringId;
    this.loading = true;
    this.$http
      .get(`/api/v1/courses/course_offerings/${id}/students`)
      .then(resp => {
        this.students = resp.data;
        this.loading = false;
      });
  }
};
</script>

<style scoped>
.max-width-250 {
  max-width: 250px;
}
</style>
