<template>
  <v-card>
    <v-card-title data-cy="course-form-title">
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-col>
          <v-text-field
            v-model="course.name"
            v-bind:label="t('courses.title')"
            name="title"
            :error-messages="nameErrors"
            data-cy="course-form-name"
          ></v-text-field>
        </v-col>
        <v-col>
          <v-textarea
            v-model="course.description"
            v-bind:label="t('courses.description')"
            name="description"
            :error-messages="descriptionErrors"
            data-cy="course-form-description"
          ></v-textarea>
        </v-col>
        <v-btn
          class="text-xs-center"
          color="primary"
          variant="text"
          size="small"
          @click="showImageChooser = true"
          :disabled="showImageChooser"
        >
          {{ t("images.actions.add-image") }}
        </v-btn>
        <v-col>
          <v-expand-transition>
            <image-chooser
              v-if="showImageChooser"
              :imageId="getImageId"
              v-on:saved="chooseImage"
              v-on:deleted="deleteImage"
              v-on:cancel="cancelImageChooser"
              v-on:missing="missingImage"
            />
          </v-expand-transition>
        </v-col>
        <br />
        <v-col>
          <v-select
            v-model="course.prerequisites"
            :items="items"
            v-bind:label="t('courses.prerequisites')"
            chips
            closable-chips
            clearable
            variant="outlined"
            multiple
            hide-selected
            return-object
            item-value="id"
            item-title="name"
            :menu-props="{ closeOnContentClick: true }"
            data-cy="course-form-prerequisites"
          >
          </v-select>
        </v-col>
      </form>
    </v-card-text>
    <v-card-actions data-cy="course-form-actions">
      <v-btn
        color="secondary"
        variant="text"
        :disabled="formDisabled"
        v-on:click="cancel"
      >
        {{ t("actions.cancel") }}
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        variant="outlined"
        v-on:click="addAnother"
        v-if="!editMode"
        :loading="addMoreLoading"
        :disabled="formDisabled"
        data-cy="add-another"
        >{{ t("actions.add-another") }}</v-btn
      >
      <v-btn
        color="primary"
        :loading="saveLoading"
        :disabled="formDisabled"
        v-on:click="save"
      >
        {{ t("actions.save") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import { isEmpty, cloneDeep } from "lodash";
import ImageChooser from "../images/ImageChooser.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;

const props = defineProps<{
  editMode: boolean;
  initialData: Record<string, any>;
  courses?: any[];
  saveLoading?: boolean;
  addMoreLoading?: boolean;
}>();

const emit = defineEmits(["cancel", "save", "addAnother"]);

const course = ref<Record<string, any>>({});
const coursesPool = ref<any[]>([]);
const addMore = ref(false);
const imageSaved = ref(false);
const showImageChooser = ref(false);
const nameErrors = ref<string[]>([]);
const descriptionErrors = ref<string[]>([]);

const items = computed(() =>
  coursesPool.value.filter(item => item.active && item.id != course.value.id)
);

const title = computed(() =>
  props.editMode ? t("actions.edit") : t("courses.new")
);

const formDisabled = computed(() =>
  !!(props.saveLoading ||
  props.addMoreLoading ||
  (showImageChooser.value && !imageSaved.value))
);

const getImageId = computed(() => {
  if (course.value.images) {
    return course.value.images.length > 0
      ? course.value.images[0].image_id
      : -1;
  } else {
    return -1;
  }
});

watch(() => props.initialData, (courseProp) => {
  console.log(courseProp);
  if (isEmpty(courseProp)) {
    clear();
  } else {
    course.value = courseProp;
    if (course.value.images && course.value.images.length > 0) {
      showImageChooser.value = true;
      imageSaved.value = true;
    } else {
      showImageChooser.value = false;
      imageSaved.value = false;
    }
  }
});

watch(() => props.courses, () => {
  loadCoursesPool();
});

function cancel() {
  emit("cancel");
}

function clear() {
  course.value = {};
  showImageChooser.value = false;
  nameErrors.value = [];
  descriptionErrors.value = [];
}

function validateForm(): boolean {
  nameErrors.value = [];
  descriptionErrors.value = [];
  let valid = true;
  if (!course.value.name) {
    nameErrors.value = [t("validations.required")];
    valid = false;
  }
  if (!course.value.description) {
    descriptionErrors.value = [t("validations.required")];
    valid = false;
  }
  return valid;
}

function addAnother() {
  addMore.value = true;
  save();
}

function save() {
  if (validateForm()) {
    let courseData = cloneDeep(course.value);
    if (addMore.value) emit("addAnother", courseData);
    else emit("save", courseData);
  }
  addMore.value = false;
}

function loadCoursesPool() {
  if (!props.courses) {
    http.get(`/api/v1/courses/courses`).then(resp => {
      coursesPool.value = resp.data;
    });
  } else {
    coursesPool.value = props.courses;
  }
}

function chooseImage(id: number) {
  course.value.newImageId = id;
  imageSaved.value = true;
}

function deleteImage() {
  showImageChooser.value = false;
  delete course.value.newImageId;
  course.value.images = [];
  imageSaved.value = false;
}

function cancelImageChooser() {
  showImageChooser.value = false;
}

function missingImage() {
  imageSaved.value = false;
}

onMounted(() => {
  loadCoursesPool();
});
</script>
