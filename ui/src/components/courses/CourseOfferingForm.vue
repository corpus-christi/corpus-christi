<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <!-- description -->
        <v-textarea
          v-model="courseOffering.description"
          v-bind:label="t('courses.description')"
          name="description"
          rows="3"
          data-cy="course-offering-description"
          :error-messages="descriptionErrors"
        ></v-textarea>

        <v-col cols="7" md="7">
          <v-text-field
            v-model="courseOffering.maxSize"
            v-bind:label="t('courses.max-size')"
            name="max-size"
            type="number"
            :error-messages="maxSizeErrors"
            data-cy="course-offering-max-size"
          ></v-text-field>
        </v-col>
      </form>
    </v-card-text>
    <v-card-actions>
      <v-btn color="secondary" variant="text" :disabled="saving" v-on:click="cancel">
        {{ t("actions.cancel") }}
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        :disabled="saving"
        :loading="saving"
        v-on:click="save"
        >{{ t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import { isEmpty, cloneDeep } from "lodash";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;

const props = defineProps<{
  editMode: boolean;
  initialData: Record<string, any>;
  course: Record<string, any>;
}>();

const emit = defineEmits(["cancel", "save"]);

const saving = ref(false);
const courseOffering = ref<Record<string, any>>({});
const descriptionErrors = ref<string[]>([]);
const maxSizeErrors = ref<string[]>([]);

const title = computed(() =>
  props.editMode ? t("actions.edit") : t("courses.new-offering")
);

watch(() => props.initialData, (courseProp) => {
  if (isEmpty(courseProp)) {
    clear();
  } else {
    courseOffering.value = courseProp;
  }
});

function cancel() {
  clear();
  emit("cancel");
}

function clear() {
  courseOffering.value = {};
  descriptionErrors.value = [];
  maxSizeErrors.value = [];
}

function validateForm(): boolean {
  descriptionErrors.value = [];
  maxSizeErrors.value = [];
  let valid = true;
  if (!courseOffering.value.description) {
    descriptionErrors.value = [t("validations.required")];
    valid = false;
  }
  if (!courseOffering.value.maxSize) {
    maxSizeErrors.value = [t("validations.required")];
    valid = false;
  }
  return valid;
}

function save() {
  if (validateForm()) {
    saving.value = true;
    let offering = cloneDeep(courseOffering.value);
    offering.courseId = props.course.id;
    saveCourseOffering(offering);
  }
}

function saveCourseOffering(offering: Record<string, any>) {
  if (props.editMode) {
    const courseOfferingId = offering.id;
    delete offering.id;

    http
      .patch(`/api/v1/courses/course_offerings/${courseOfferingId}`, offering)
      .then(resp => {
        console.log("EDITED", resp);
        emit("save", resp.data);
      })
      .catch(err => {
        console.error("FAILURE", err.response);
        emit("save", err);
      })
      .finally(() => {
        saving.value = false;
      });
  } else {
    offering.active = true;
    http
      .post("/api/v1/courses/course_offerings", offering)
      .then(resp => {
        console.log("ADDED", resp);
        emit("save", resp.data);
      })
      .catch(err => {
        console.error("FAILURE", err.response);
        emit("save", err);
      })
      .finally(() => {
        saving.value = false;
      });
  }
}
</script>
