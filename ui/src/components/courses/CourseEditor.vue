<template>
  <v-card>
    <v-card-title data-cy="course-editor-title">
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text> <CourseForm ref="form" :course="course" :editMode="editMode" :initialData="course" @cancel="cancel" @save="handleSave" /> </v-card-text>
    <v-card-actions data-cy="course-editor-actions">
      <v-btn color="secondary" variant="text" :disabled="saving" v-on:click="cancel">
        {{ t("actions.cancel") }}
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        :disabled="saving"
        :loading="saving"
        v-on:click="save"
      >
        {{ t("actions.save") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import { isEmpty, cloneDeep } from "lodash";
import CourseForm from "./CourseForm.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;

const props = defineProps<{
  editMode: boolean;
  initialData: Record<string, any>;
}>();

const emit = defineEmits(["cancel", "save"]);

const course = ref<Record<string, any>>({});
const saving = ref(false);

const title = computed(() =>
  props.editMode ? t("actions.edit") : t("courses.new")
);

watch(() => props.initialData, (courseProp) => {
  if (isEmpty(courseProp)) {
    clear();
  } else {
    course.value = courseProp;
  }
});

function cancel() {
  clear();
  emit("cancel");
}

function clear() {
  course.value = {};
}

function handleSave(savedCourse: any) {
  emit("save", savedCourse);
}

function save() {
  saving.value = true;
  let courseData = cloneDeep(course.value);
  saveCourse(courseData);
}

function saveCourse(courseData: Record<string, any>) {
  let courseAttrs = {
    description: courseData.description,
    name: courseData.name
  };

  if (props.editMode) {
    let promises: Promise<any>[] = [];
    promises.push(
      http
        .patch(`/api/v1/courses/courses/${courseData.id}`, courseAttrs)
        .then(resp => {
          console.log("EDITED", resp);
          return resp;
        })
    );
    promises.push(
      http.patch(`/api/v1/courses/courses/${courseData.id}/prerequisites`, {
        prerequisites: courseData.prerequisites
          ? courseData.prerequisites.map((prereq: any) => prereq.id)
          : []
      })
    );

    Promise.all(promises)
      .then(resps => {
        let newCourse = resps[0].data;
        newCourse.prerequisites = courseData.prerequisites;
        emit("save", newCourse);
      })
      .catch(err => {
        console.error("FAILURE", err.response);
        emit("save", err);
      })
      .finally(() => {
        saving.value = false;
      });
  } else {
    (courseAttrs as any).active = true;
    let newCourse: any;
    http
      .post("/api/v1/courses/courses", courseAttrs)
      .then(resp => {
        console.log("ADDED", resp);
        newCourse = resp.data;
        newCourse.prerequisites = courseData.prerequisites;

        return http.patch(`/api/v1/courses/courses/${newCourse.id}/prerequisites`, {
          prerequisites: courseData.prerequisites
            ? courseData.prerequisites.map((prereq: any) => prereq.id)
            : []
        });
      })
      .then(resp => {
        console.log("PREREQS", resp);
        emit("save", newCourse);
      })
      .catch(err => {
        console.error("FAILURE", err);
        emit("save", err);
      })
      .finally(() => {
        saving.value = false;
      });
  }
}
</script>
