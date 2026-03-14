<template>
  <div>
    <!-- Header -->
    <v-toolbar class="pa-1">
      <v-row justify="space-between">
        <v-col shrink class="align-self-center">
          <v-toolbar-title>{{ t("courses.course-offering") }}</v-toolbar-title>
        </v-col>
        <v-spacer></v-spacer>
        <v-col shrink>
          <v-btn color="primary" variant="elevated" v-on:click.stop="newCourseOffering">
            <v-icon left>library_add</v-icon>
            {{ t("courses.new-offering") }}
          </v-btn>
        </v-col>
      </v-row>
      <template #extension>
        <v-row justify="space-between" align="center">
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

    <!-- Table of existing people -->
    <v-data-table
      :headers="headers"
      :search="search"
      :items="showCourseOfferings"
      class="elevation-1"
      :items-per-page-options="rowsPerPageItem"
    >
      <template #item="{ item }">
        <tr>
          <td class="hover-hand" @click="clickThrough(item)">
            {{ item.description }}
          </td>
          <td class="hover-hand" @click="clickThrough(item)">
            {{ item.maxSize }}
          </td>
          <td>
            <CourseOfferingAdminActions
              v-bind:courseOffering="item"
              display-context="compact"
              v-on:action="dispatchAction($event, item)"
            />
          </td>
        </tr>
      </template>
    </v-data-table>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false">
          {{ t("actions.close") }}
        </v-btn>
      </template>
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
            v-on:click="deactivate(deactivateDialog.courseOffering)"
            color="primary"
            variant="elevated"
            :disabled="deactivateDialog.loading"
            :loading="deactivateDialog.loading"
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
import { useRouter } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import CourseOfferingForm from "./CourseOfferingForm.vue";
import CourseOfferingAdminActions from "./actions/CourseOfferingAdminActions.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const router = useRouter();

const props = defineProps<{
  course: any;
}>();

const courseOfferingDialog = ref({
  show: false,
  editMode: false,
  courseOffering: {} as any
});

const deactivateDialog = ref({
  show: false,
  courseOffering: {} as any,
  loading: false
});

const snackbar = ref({
  show: false,
  text: ""
});

const rowsPerPageItem = [10, 15, 25, { title: "All", value: -1 }];
const courseOfferings = ref<any[]>([]);
const selected = ref<any[]>([]);
const search = ref("");
const viewStatus = ref("active");

const headers = computed(() => [
  { title: t("courses.description"), value: "description", width: "80%" },
  { title: t("courses.max-size"), value: "maxSize", width: "20%" },
  { title: t("actions.header"), sortable: false }
]);

const options = computed(() => [
  { title: t("actions.view-active"), value: "active" },
  { title: t("actions.view-archived"), value: "archived" },
  { title: t("actions.view-all"), value: "all" }
]);

const showCourseOfferings = computed(() => {
  switch (viewStatus.value) {
    case "active":
      return courseOfferings.value.filter(co => co.active);
    case "archived":
      return courseOfferings.value.filter(co => !co.active);
    case "all":
    default:
      return courseOfferings.value;
  }
});

function clickThrough(courseOffering: any) {
  router.push({
    name: "course-offering-details",
    params: { offeringId: courseOffering.id }
  });
}

function dispatchAction(actionName: string, courseOffering: any) {
  switch (actionName) {
    case "edit":
      editCourseOffering(courseOffering);
      break;
    case "deactivate":
      confirmDeactivate(courseOffering);
      break;
    case "activate":
      activate(courseOffering);
      break;
    default:
      break;
  }
}

function activateCourseOfferingDialog(courseOffering: any = {}, editMode = false) {
  courseOfferingDialog.value.editMode = editMode;
  courseOfferingDialog.value.courseOffering = courseOffering;
  courseOfferingDialog.value.show = true;
}

function editCourseOffering(courseOffering: any) {
  activateCourseOfferingDialog({ ...courseOffering }, true);
}

function newCourseOffering() {
  activateCourseOfferingDialog();
}

function cancelCourseOffering() {
  courseOfferingDialog.value.show = false;
}

function confirmDeactivate(courseOffering: any) {
  deactivateDialog.value.show = true;
  deactivateDialog.value.courseOffering = courseOffering;
}

function cancelDeactivate() {
  deactivateDialog.value.show = false;
}

function deactivate(courseOffering: any) {
  deactivateDialog.value.loading = true;
  http
    .patch(`/api/v1/courses/course_offerings/${courseOffering.id}`, { active: false })
    .then(resp => {
      console.log("EDITED", resp);
      Object.assign(courseOffering, resp.data);
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

function activate(courseOffering: any) {
  http
    .patch(`/api/v1/courses/course_offerings/${courseOffering.id}`, { active: true })
    .then(resp => {
      console.log("EDITED", resp);
      Object.assign(courseOffering, resp.data);
      snackbar.value.text = t("courses.reactivated");
      snackbar.value.show = true;
    })
    .catch(() => {
      snackbar.value.text = t("courses.update-failed");
      snackbar.value.show = true;
    });
}

function saveCourseOffering(courseOffering: any) {
  if (courseOffering instanceof Error) {
    snackbar.value.text = courseOfferingDialog.value.editMode
      ? t("courses.update-failed")
      : t("courses.add-failed");
    snackbar.value.show = true;
    courseOfferingDialog.value.show = false;
    return;
  }

  if (courseOfferingDialog.value.editMode) {
    const idx = courseOfferings.value.findIndex(c => c.id === courseOffering.id);
    Object.assign(courseOfferings.value[idx], courseOffering);
    snackbar.value.text = t("courses.updated");
  } else {
    courseOfferings.value.push(courseOffering);
    snackbar.value.text = t("courses.added");
  }

  snackbar.value.show = true;
  courseOfferingDialog.value.show = false;
}

onMounted(() => {
  courseOfferings.value = props.course.course_offerings;
});
</script>

<style scoped>
.hover-hand {
  cursor: pointer;
}

.max-width-250 {
  max-width: 250px;
}
</style>
