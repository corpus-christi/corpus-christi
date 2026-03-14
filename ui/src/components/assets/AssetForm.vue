<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-textarea
          rows="3"
          v-model="asset.description"
          v-bind:label="t('assets.description')"
          name="description"
          :error-messages="descriptionErrors"
          data-cy="description"
        ></v-textarea>

        <EntitySearch
          location
          name="location"
          v-model="asset.location"
          v-bind:error-messages="locationErrors"
        />
      </form>
    </v-card-text>
    <v-card-actions>
      <v-btn
        color="secondary"
        variant="text"
        v-on:click="cancel"
        :disabled="formDisabled"
        data-cy="form-cancel"
        >{{ t("actions.cancel") }}</v-btn
      >
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        variant="outlined"
        v-on:click="addAnother"
        v-if="editMode === false"
        :loading="addMoreLoading"
        :disabled="formDisabled"
        data-cy="form-addanother"
        >{{ t("actions.add-another") }}</v-btn
      >
      <v-btn
        color="primary"
        v-on:click="save"
        :loading="saveLoading"
        :disabled="formDisabled"
        data-cy="form-save"
        >{{ t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useI18n } from "vue-i18n";
import { isEmpty } from "lodash";
import EntitySearch from "../EntitySearch.vue";

const { t } = useI18n();

const props = defineProps<{
  editMode: boolean;
  initialData: Record<string, any>;
  saveLoading?: boolean;
  addMoreLoading?: boolean;
}>();

const emit = defineEmits(["cancel", "save", "addAnother"]);

const asset = ref<Record<string, any>>({});
const addMore = ref(false);

const descriptionErrors = ref<string[]>([]);
const locationErrors = ref<string[]>([]);

watch(() => props.initialData, (assetProp) => {
  if (isEmpty(assetProp)) {
    clear();
  } else {
    asset.value = { ...assetProp };
  }
});

const title = computed(() =>
  props.editMode ? t("assets.edit-asset") : t("assets.create-asset")
);

const formDisabled = computed(() => !!(props.saveLoading || props.addMoreLoading));

function validateForm(): boolean {
  descriptionErrors.value = [];
  locationErrors.value = [];
  let valid = true;
  if (!asset.value.description) {
    descriptionErrors.value = [t("validations.required")];
    valid = false;
  }
  if (!asset.value.location) {
    locationErrors.value = [t("validations.required")];
    valid = false;
  }
  return valid;
}

function cancel() {
  emit("cancel");
}

function clear() {
  delete asset.value.location;
  for (let key of Object.keys(asset.value)) {
    asset.value[key] = "";
  }
  descriptionErrors.value = [];
  locationErrors.value = [];
}

function save() {
  if (validateForm()) {
    asset.value.active = true;
    if (addMore.value) emit("addAnother", asset.value);
    else emit("save", asset.value);
  }
  addMore.value = false;
}

function addAnother() {
  addMore.value = true;
  save();
}
</script>
