<template>
  <div>
    <v-row wrap>
      <v-col cols="12">
        <v-btn
          variant="outlined"
          color="primary"
          v-on:click="router.push({ name: 'all-courses' })"
          ><v-icon>arrow_back</v-icon>{{ t("actions.back") }}</v-btn
        >
      </v-col>
      <v-col cols="12" sm="12" md="3">
        <v-card>
          <template v-if="loading">
            <v-container fill-height fluid>
              <v-row align="center" justify="center">
                <v-progress-circular color="primary" indeterminate />
              </v-row>
            </v-container>
          </template>
          <template v-else>
            <v-card-title class="d-block">
              <h5 class="headline">{{ course.name }}</h5>
              <span class="caption" v-if="!course.active">
                <v-icon size="small">archive</v-icon>
                {{ t("courses.is-archived") }}
              </span>
            </v-card-title>
            <v-card-text> {{ course.description }} </v-card-text>
            <v-card-text> <v-img :src="fetchImage"> </v-img> </v-card-text>
            <v-card-actions>
              <v-btn
                variant="text"
                color="primary"
                @click="editCourse"
                data-cy="course-details-edit-button"
              >
                <v-icon start>edit</v-icon>
                {{ t("actions.edit") }}
              </v-btn>
            </v-card-actions>
          </template>
        </v-card>
        <v-card class="mt-2" v-if="!loading">
          <template v-if="course.prerequisites && course.prerequisites.length > 0">
            <v-card-title>
              <h5 class="headline">{{ t("courses.prerequisites") }}</h5>
            </v-card-title>
            <v-card-text>
              <v-list density="compact">
                <v-list-item
                  v-for="prereq of course.prerequisites"
                  :key="prereq.id"
                  :to="{
                    name: 'course-details',
                    params: { courseId: prereq.id }
                  }"
                >
                  {{ prereq.name }}
                </v-list-item>
              </v-list>
            </v-card-text>
          </template>
          <template v-else>
            <v-card-text> {{ t("courses.no-prerequisites") }} </v-card-text>
          </template>
        </v-card>
      </v-col>
      <v-col cols="12" sm="12" md="9" class="pl-2" v-if="!loading">
        <CourseOfferingsTable :course="course" />
      </v-col>
    </v-row>

    <v-dialog
      v-model="courseDialog.show"
      max-width="500px"
      persistent
      scrollable
      data-cy="course-editor"
    >
      <CourseForm
        :editMode="true"
        :initialData="courseDialog.course"
        @cancel="cancelCourse"
        @save="saveCourse"
      />
    </v-dialog>

    <v-snackbar v-model="snackbar.show" data-cy="courses-table-snackbar">
      {{ snackbar.text }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false">{{
          t("actions.close")
        }}</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter, useRoute } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import CourseOfferingsTable from "./CourseOfferingsTable.vue";
import CourseForm from "./CourseForm.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const router = useRouter();
const route = useRoute();

const props = defineProps<{
  courseId: string | number;
}>();

const course = ref<Record<string, any>>({ prerequisites: [] });
const loading = ref(true);
const loadingFailed = ref(false);
const courseDialog = ref({
  show: false,
  course: {} as Record<string, any>
});
const snackbar = ref({ show: false, text: "" });

const fetchImage = computed(() => {
  if (course.value.images && course.value.images.length > 0) {
    return `/api/v1/images/${course.value.images[0].image.id}?${Math.random()}`;
  } else {
    return "";
  }
});

watch(route, () => {
  loadCourse();
});

onMounted(() => {
  loadCourse();
});

function loadCourse() {
  loading.value = true;
  loadingFailed.value = false;
  http
    .get(`/api/v1/courses/courses/${props.courseId}`)
    .then(resp => {
      course.value = resp.data;
    })
    .catch(() => {
      loadingFailed.value = true;
    })
    .finally(() => {
      loading.value = false;
    });
}

function editCourse() {
  courseDialog.value.course = { ...course.value };
  courseDialog.value.show = true;
}

function cancelCourse() {
  courseDialog.value.show = false;
}

async function saveCourse(updatedCourse: any) {
  if (updatedCourse instanceof Error) {
    snackbar.value.text = t("courses.update-failed");
    snackbar.value.show = true;
    return;
  }

  let courseAttrs = {
    description: updatedCourse.description,
    name: updatedCourse.name
  };

  let newImageId = updatedCourse.newImageId;
  let oldImageId = await getOldImageId(updatedCourse.id);

  var prereqMap: number[] = [];
  if (updatedCourse.prerequisites) {
    prereqMap = updatedCourse.prerequisites.map((prereq: any) => prereq.id);
  }

  let promises: Promise<any>[] = [];
  promises.push(
    http
      .patch(`/api/v1/courses/courses/${updatedCourse.id}`, courseAttrs)
      .then(resp => {
        console.log("EDITED", resp);
        return resp;
      })
  );

  if (newImageId) {
    if (oldImageId) {
      promises.push(
        http.put(
          `/api/v1/courses/${updatedCourse.id}/images/${newImageId}?old=${oldImageId}`
        )
      );
    } else {
      promises.push(
        http.post(`/api/v1/courses/${updatedCourse.id}/images/${newImageId}`)
      );
    }
  } else {
    if (oldImageId) {
      promises.push(
        http.delete(`/api/v1/courses/${updatedCourse.id}/images/${oldImageId}`)
      );
    }
  }

  promises.push(
    http.patch(`/api/v1/courses/courses/${updatedCourse.id}/prerequisites`, {
      prerequisites: prereqMap
    })
  );

  Promise.all(promises)
    .then(resps => {
      let newCourse = resps[0].data;
      newCourse.prerequisites = updatedCourse.prerequisites;
      cancelCourse();
      loadCourse();
      snackbar.value.text = t("courses.updated");
      snackbar.value.show = true;
    })
    .catch(err => {
      console.error("FAILURE", err.response);
      snackbar.value.text = t("courses.update-failed");
      snackbar.value.show = true;
    });
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
</script>

<style></style>
