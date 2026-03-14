<template>
  <div>
    <v-toolbar class="pa-1">
      <v-row justify="space-between" no-gutters>
        <v-col cols="auto" class="align-self-center">
          <v-toolbar-title>{{ t("courses.students") }}</v-toolbar-title>
        </v-col>
        <v-spacer></v-spacer>
        <v-col cols="auto">
          <v-btn
            color="primary"
            v-on:click.stop="newStudent"
            class="hidden-xs-only mr-2"
          >
            <v-icon dark start>add</v-icon>
            <span class="mr-1"> {{ t("actions.add-person") }} </span>
          </v-btn>
          <v-btn
            class="hidden-sm-and-up"
            color="primary"
            icon
            v-on:click.stop="newStudent"
            data-cy="add-student-small"
          >
            <v-icon dark>add</v-icon>
          </v-btn>
        </v-col>
      </v-row>
      <template #extension>
        <v-row justify="space-between" align="center" no-gutters>
          <v-col>
            <v-text-field
              v-model="search"
              append-icon="search"
              v-bind:label="t('actions.search')"
              single-line
              hide-details
              class="max-width-250 mr-2"
            ></v-text-field>
          </v-col>
          <v-select
            v-model="viewStatus"
            :items="options"
            solo
            hide-details
            class="max-width-250 mr-2"
          >
          </v-select>
        </v-row>
      </template>
    </v-toolbar>
    <v-data-table
      :headers="headers"
      :items="showStudents"
      :search="search"
      :loading="loading"
      class="elevation-1"
    >
      <template #item="{ item }">
        <tr>
          <td>{{ item.person?.firstName }}</td>
          <td>{{ item.person?.lastName }}</td>
          <td>{{ item.person?.email }}</td>
          <td>{{ item.person?.phone }}</td>
          <td>
            <StudentsAdminActions
              v-bind:student="item"
              display-context="compact"
              v-on:action="dispatchAction($event, item)"
            />
          </td>
        </tr>
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
        <v-card-text>{{ t("courses.confirm-archive") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelDeactivate"
            color="secondary"
            variant="text"
            :disabled="deactivateDialog.loading"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deactivate(deactivateDialog.student)"
            color="primary"
            :disabled="deactivateDialog.loading"
            :loading="deactivateDialog.loading"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Confirm Dialog -->
    <v-dialog v-model="confirmDialog.show" max-width="400px">
      <v-card>
        <v-card-text>{{ t("courses.confirm-student") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelConfirmDialog"
            color="secondary"
            variant="text"
            :disabled="confirmDialog.confirming"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="rejectStudent(confirmDialog.student)"
            color="accent"
            :loading="confirmDialog.confirming"
            >{{ t("courses.reject") }}</v-btn
          >
          <v-btn
            v-on:click="confirmStudent(confirmDialog.student)"
            color="primary"
            :disabled="confirmDialog.confirming"
            :loading="confirmDialog.confirming"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import StudentsForm from "./StudentsForm.vue";
import StudentsAdminActions from "./actions/StudentsAdminActions.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;

const props = defineProps<{
  offeringId?: any;
}>();

const search = ref("");
const students = ref<any[]>([]);
const viewStatus = ref("active");
const loading = ref(false);

const newStudentDialog = ref({
  show: false,
  newStudent: {} as Record<string, any>,
  saving: false
});

const deactivateDialog = ref({
  show: false,
  student: {} as Record<string, any>,
  loading: false
});

const confirmDialog = ref({
  show: false,
  student: {} as Record<string, any>,
  confirming: false
});

const snackbar = ref({ show: false, text: "" });

const headers = computed(() => [
  { title: t("person.name.first"), value: "person.firstName", width: "20%" },
  { title: t("person.name.last"), value: "person.lastName", width: "20%" },
  { title: t("person.email"), value: "person.email", width: "22.5%" },
  { title: t("person.phone"), value: "person.phone", width: "22.5%" },
  { title: t("actions.header"), sortable: false }
]);

const options = computed(() => [
  { title: t("actions.view-active"), value: "active" },
  { title: t("actions.view-archived"), value: "archived" },
  { title: t("actions.view-all"), value: "all" }
]);

const showStudents = computed(() => {
  switch (viewStatus.value) {
    case "active":
      return students.value.filter(student => student.active);
    case "archived":
      return students.value.filter(student => !student.active);
    case "all":
    default:
      return students.value;
  }
});

function activateNewStudentDialog(newStudent: Record<string, any> = {}) {
  newStudentDialog.value.show = true;
  newStudentDialog.value.newStudent = newStudent;
}

function cancelNewStudent() {
  newStudentDialog.value.show = false;
}

function newStudent() {
  activateNewStudentDialog();
}

function saveNewStudent(person: any) {
  newStudentDialog.value.saving = true;

  let newStudent: Record<string, any> = {};
  newStudent.confirmed = true;
  newStudent.offeringId = props.offeringId;
  newStudent.studentId = person.id;
  newStudent.active = true;

  http
    .post(`/api/v1/courses/course_offerings/${newStudent.studentId}`, newStudent)
    .then(resp => {
      console.log("ADDED", resp);
      students.value.push(resp.data);
      snackbar.value.text = t("courses.added");
      snackbar.value.show = true;
    })
    .catch(err => {
      console.error("FAILURE", err.response);
      snackbar.value.text = t("courses.add-failed");
      snackbar.value.show = true;
    })
    .finally(() => {
      newStudentDialog.value.show = false;
      newStudentDialog.value.saving = false;
    });
}

function dispatchAction(actionName: string, student: any) {
  switch (actionName) {
    case "deactivate":
      confirmDeactivate(student);
      break;
    case "activate":
      activate(student);
      break;
    case "confirm":
      showConfirmDialog(student);
      break;
    default:
      break;
  }
}

function showConfirmDialog(student: any) {
  confirmDialog.value.show = true;
  confirmDialog.value.student = student;
}

function rejectStudent(student: any) {
  confirmDialog.value.confirming = true;
  http
    .patch(`/api/v1/courses/students/${student.id}`, { active: false })
    .then(resp => {
      console.log("EDITED", resp);
      Object.assign(student, resp.data);
      snackbar.value.text = t("courses.archived");
      snackbar.value.show = true;
    })
    .catch(() => {
      snackbar.value.text = t("courses.update-failed");
      snackbar.value.show = true;
    })
    .finally(() => {
      confirmDialog.value.confirming = false;
      confirmDialog.value.show = false;
    });
}

function confirmStudent(student: any) {
  http
    .patch(`/api/v1/courses/students/${student.id}`, { confirmed: true })
    .then(resp => {
      console.log("EDITED", resp);
      Object.assign(student, resp.data);
      snackbar.value.text = t("courses.reactivated");
      snackbar.value.show = true;
    })
    .catch(() => {
      snackbar.value.text = t("courses.update-failed");
      snackbar.value.show = true;
    })
    .finally(() => {
      confirmDialog.value.show = false;
      confirmDialog.value.confirming = false;
    });
}

function cancelConfirmDialog() {
  confirmDialog.value.show = false;
}

function confirmDeactivate(student: any) {
  deactivateDialog.value.show = true;
  deactivateDialog.value.student = student;
}

function cancelDeactivate() {
  deactivateDialog.value.show = false;
}

function deactivate(student: any) {
  deactivateDialog.value.loading = true;
  http
    .patch(`/api/v1/courses/students/${student.id}`, { active: false })
    .then(resp => {
      console.log("EDITED", resp);
      Object.assign(student, resp.data);
      snackbar.value.text = t("courses.archived");
      snackbar.value.show = true;
    })
    .catch(() => {
      snackbar.value.text = t("courses.update-failed");
      snackbar.value.show = true;
    })
    .finally(() => {
      deactivateDialog.value.loading = false;
      deactivateDialog.value.show = false;
    });
}

function activate(student: any) {
  http
    .patch(`/api/v1/courses/students/${student.id}`, { active: true })
    .then(resp => {
      console.log("EDITED", resp);
      Object.assign(student, resp.data);
      snackbar.value.text = t("courses.reactivated");
      snackbar.value.show = true;
    })
    .catch(() => {
      snackbar.value.text = t("courses.update-failed");
      snackbar.value.show = true;
    });
}

onMounted(() => {
  const id = props.offeringId;
  loading.value = true;
  http
    .get(`/api/v1/courses/course_offerings/${id}/students`)
    .then(resp => {
      students.value = resp.data;
      loading.value = false;
    });
});
</script>

<style scoped>
.max-width-250 {
  max-width: 250px;
}
</style>
