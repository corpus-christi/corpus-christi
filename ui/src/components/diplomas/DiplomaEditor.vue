<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-text-field
          v-model="diploma.name"
          v-bind:label="t('diplomas.title')"
          name="title"
          :error-messages="nameErrors"
          data-cy="diplomas-form-name"
        ></v-text-field>
        <v-textarea
          v-model="diploma.description"
          v-bind:label="t('diplomas.description')"
          name="description"
          :error-messages="descriptionErrors"
          data-cy="diploma-form-description"
        ></v-textarea>
        <br />
        <v-select
          v-model="diploma.courseList"
          :items="items"
          v-bind:label="t('diplomas.courses')"
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
        ></v-select>
      </form>
    </v-card-text>
    <v-card-actions>
      <v-btn
        color="secondary"
        variant="text"
        :disabled="formDisabled"
        v-on:click="cancel"
        >{{ t("actions.cancel") }}</v-btn
      >
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        variant="outlined"
        v-on:click="addAnother"
        v-if="!editMode"
        :loading="addMoreLoading"
        :disabled="formDisabled"
        data-cy="form-addanother"
        >{{ t("actions.add-another") }}</v-btn
      >
      <v-btn
        color="primary"
        :disabled="formDisabled"
        :loading="saveLoading"
        data-cy="form-save"
        v-on:click="save"
        >{{ t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import { isEmpty } from "lodash";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;

const props = defineProps<{
  initialData: Record<string, any>;
  editMode: boolean;
  saveLoading?: boolean;
  addMoreLoading?: boolean;
}>();

const emit = defineEmits(["cancel", "save", "addAnother"]);

const coursesPool = ref<any[]>([]);
const diploma = ref<Record<string, any>>({});
const addMore = ref(false);
const nameErrors = ref<string[]>([]);
const descriptionErrors = ref<string[]>([]);

const title = computed(() =>
  props.editMode ? t("actions.edit") : t("diplomas.new")
);

const items = computed(() => coursesPool.value);

const formDisabled = computed(() => !!(props.saveLoading || props.addMoreLoading));

watch(() => props.initialData, (diplomaProp) => {
  if (isEmpty(diplomaProp)) {
    clear();
  } else {
    diploma.value = diplomaProp;
  }
});

function cancel() {
  emit("cancel");
}

function clear() {
  diploma.value = {};
  nameErrors.value = [];
  descriptionErrors.value = [];
}

function validateForm(): boolean {
  nameErrors.value = [];
  descriptionErrors.value = [];
  let valid = true;
  if (!diploma.value.name) {
    nameErrors.value = [t("validations.required")];
    valid = false;
  }
  if (!diploma.value.description) {
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
    if (addMore.value) emit("addAnother", diploma.value);
    else emit("save", diploma.value);
  }
  addMore.value = false;
}

onMounted(() => {
  http
    .get("/api/v1/courses/courses")
    .then(resp => (coursesPool.value = resp.data));
});
</script>
