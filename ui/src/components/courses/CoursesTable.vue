<template>
  <div>
    <!-- Header -->
    <v-toolbar class="pa-1">
      <v-row justify="space-between" no-gutters>
        <v-col cols="auto" class="align-self-center">
          <v-toolbar-title>{{ t("courses.course") }}</v-toolbar-title>
        </v-col>
        <v-spacer></v-spacer>
        <v-col cols="auto">
          <v-btn
            color="primary"
            v-on:click.stop="newCourse"
            data-cy="courses-table-new"
            class="hidden-xs-only mr-2"
          >
            <v-icon start>library_add</v-icon>
            <span class="mr-1"> {{ t("courses.new") }} </span>
          </v-btn>
          <v-btn
            class="hidden-sm-and-up"
            color="primary"
            icon
            v-on:click.stop="newCourse"
            data-cy="add-courseOffering-small"
          >
            <v-icon dark>add</v-icon>
          </v-btn>
        </v-col>
      </v-row>
      <template #extension>
        <v-row justify="space-between" align="center" no-gutters>
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="t('actions.search')"
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
        </v-row>
      </template>
    </v-toolbar>

    <!-- Table of existing courses -->
    <v-data-table
      :headers="headers"
      :search="search"
      :items="showCourses"
      :loading="!tableLoaded"
      class="elevation-1"
      data-cy="courses-table"
    >
      <template #item="{ item }">
        <tr>
          <td class="hover-hand" @click="clickThrough(item)">
            {{ item.name }}
          </td>
          <td class="hover-hand" @click="clickThrough(item)">
            {{ item.description }}
          </td>
          <td>
            <CourseAdminActions
              v-bind:course="item"
              display-context="compact"
              v-on:action="dispatchAction($event, item)"
            />
          </td>
        </tr>
      </template>
    </v-data-table>

    <v-snackbar v-model="snackbar.show" data-cy="courses-table-snackbar">
      {{ snackbar.text }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false">{{
          t("actions.close")
        }}</v-btn>
      </template>
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
        <v-card-text>{{ t("courses.confirm-archive") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelDeactivate"
            color="secondary"
            variant="text"
            :disabled="deactivateDialog.loading"
          >
            {{ t("actions.cancel") }}
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deactivate(deactivateDialog.course)"
            color="primary"
            :disabled="deactivateDialog.loading"
            :loading="deactivateDialog.loading"
          >
            {{ t("actions.confirm") }}
          </v-btn>
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
import CourseForm from "./CourseForm.vue";
import CourseAdminActions from "./actions/CourseAdminActions.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const router = useRouter();

const courseDialog = ref({
  show: false,
  editMode: false,
  course: {} as Record<string, any>,
  saveLoading: false,
  addMoreLoading: false
});

const deactivateDialog = ref({
  show: false,
  course: {} as Record<string, any>,
  loading: false
});

const snackbar = ref({ show: false, text: "" });

const courses = ref<any[]>([]);
const tableLoaded = ref(false);
const addMore = ref(false);
const search = ref("");
const viewStatus = ref("active");

const headers = computed(() => [
  { title: t("courses.title"), value: "name", width: "40%" },
  { title: t("courses.description"), value: "description", width: "60%" },
  { title: t("actions.header"), sortable: false }
]);

const options = computed(() => [
  { title: t("actions.view-active"), value: "active" },
  { title: t("actions.view-archived"), value: "archived" },
  { title: t("actions.view-all"), value: "all" }
]);

const showCourses = computed(() => {
  switch (viewStatus.value) {
    case "active":
      return courses.value.filter(course => course.active);
    case "archived":
      return courses.value.filter(course => !course.active);
    case "all":
    default:
      return courses.value;
  }
});

function clickThrough(course: any) {
  router.push({ name: "course-details", params: { courseId: course.id } });
}

function dispatchAction(actionName: string, course: any) {
  switch (actionName) {
    case "edit":
      editCourse(course);
      break;
    case "deactivate":
      confirmDeactivate(course);
      break;
    case "activate":
      activate(course);
      break;
    default:
      break;
  }
}

function activateCourseDialog(course: Record<string, any> = {}, editMode = false) {
  courseDialog.value.editMode = editMode;
  courseDialog.value.course = course;
  courseDialog.value.show = true;
}

function editCourse(course: any) {
  activateCourseDialog({ ...course }, true);
}

function newCourse() {
  activateCourseDialog();
}

function confirmDeactivate(course: any) {
  deactivateDialog.value.show = true;
  deactivateDialog.value.course = course;
}

function cancelDeactivate() {
  deactivateDialog.value.show = false;
}

function deactivate(course: any) {
  deactivateDialog.value.loading = true;
  http
    .patch(`/api/v1/courses/courses/${course.id}`, { active: false })
    .then(resp => {
      console.log("EDITED", resp);
      Object.assign(course, resp.data);
      showSnackbar(t("courses.archived"));
    })
    .catch(() => {
      showSnackbar(t("courses.update-failed"));
    })
    .finally(() => {
      deactivateDialog.value.loading = false;
      deactivateDialog.value.show = false;
    });
}

function activate(course: any) {
  http
    .patch(`/api/v1/courses/courses/${course.id}`, { active: true })
    .then(resp => {
      console.log("EDITED", resp);
      Object.assign(course, resp.data);
      showSnackbar(t("courses.reactivated"));
    })
    .catch(() => {
      showSnackbar(t("courses.update-failed"));
    });
}

function clearCourse() {
  addMore.value = false;
  courseDialog.value.saveLoading = false;
  courseDialog.value.addMoreLoading = false;
  courseDialog.value.course = {};
}

function cancelCourse() {
  addMore.value = false;
  courseDialog.value.show = false;
  courseDialog.value.saveLoading = false;
  courseDialog.value.addMoreLoading = false;
}

function addAnother(course: any) {
  addMore.value = true;
  courseDialog.value.addMoreLoading = true;
  saveCourse(course);
}

function save(course: any) {
  courseDialog.value.saveLoading = true;
  saveCourse(course);
}

async function saveCourse(course: any) {
  let courseAttrs: Record<string, any> = {
    description: course.description,
    name: course.name
  };

  let newImageId = course.newImageId;
  let oldImageId = await getOldImageId(course.id);

  var prereqMap: number[] = [];
  if (course.prerequisites) {
    prereqMap = course.prerequisites.map((prereq: any) => prereq.id);
  }

  if (courseDialog.value.editMode) {
    let promises: Promise<any>[] = [];
    promises.push(
      http
        .patch(`/api/v1/courses/courses/${course.id}`, courseAttrs)
        .then(resp => {
          console.log("EDITED", resp);
          return resp;
        })
    );

    if (newImageId) {
      if (oldImageId) {
        promises.push(
          http.put(`/api/v1/courses/${course.id}/images/${newImageId}?old=${oldImageId}`)
        );
      } else {
        promises.push(
          http.post(`/api/v1/courses/${course.id}/images/${newImageId}`)
        );
      }
    } else {
      if (oldImageId) {
        promises.push(
          http.delete(`/api/v1/courses/${course.id}/images/${oldImageId}`)
        );
      }
    }

    promises.push(
      http.patch(`/api/v1/courses/courses/${course.id}/prerequisites`, {
        prerequisites: prereqMap
      })
    );

    Promise.all(promises)
      .then(resps => {
        let newCourse = resps[0].data;
        newCourse.prerequisites = course.prerequisites;
        const idx = courses.value.findIndex(c => c.id === course.id);
        Object.assign(courses.value[idx], course);
        cancelCourse();
        refreshCourseList();
        showSnackbar(t("courses.updated"));
      })
      .catch(err => {
        console.error("FAILURE", err.response);
        courseDialog.value.saveLoading = false;
        showSnackbar(t("courses.update-failed"));
      });
  } else {
    courseAttrs.active = true;
    let newCourse: any;
    http
      .post("/api/v1/courses/courses", courseAttrs)
      .then(resp => {
        console.log("ADDED", resp);
        newCourse = resp.data;
        newCourse.prerequisites = course.prerequisites;

        return http.patch(`/api/v1/courses/courses/${newCourse.id}/prerequisites`, {
          prerequisites: prereqMap
        });
      })
      .then(resp => {
        console.log("PREREQS", resp);
        return newImageId
          ? http.post(`/api/v1/courses/${newCourse.id}/images/${newImageId}`)
          : null;
      })
      .then(resp => {
        console.log("IMAGE ADDED TO COURSE", resp);
        courses.value.push(course);
        showSnackbar(t("courses.added"));
        if (addMore.value) {
          clearCourse();
        } else {
          cancelCourse();
        }
        refreshCourseList();
      })
      .catch(err => {
        console.error("FAILURE", err);
        courseDialog.value.saveLoading = false;
        courseDialog.value.addMoreLoading = false;
        showSnackbar(t("courses.add-failed"));
      });
  }
}

async function getOldImageId(id: any) {
  if (!id) return null;
  return await http
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
}

function showSnackbar(message: string) {
  snackbar.value.text = message;
  snackbar.value.show = true;
}

function refreshCourseList() {
  http.get("/api/v1/courses/courses?include_images=1").then(resp => {
    courses.value = resp.data;
    tableLoaded.value = true;
  });
}

onMounted(() => {
  refreshCourseList();
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
