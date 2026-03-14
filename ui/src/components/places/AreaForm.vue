<template>
  <v-card>
    <v-card-text>
      <span class="headling">{{ t("places.area.create-area") }}</span>
      <v-col>
        <v-text-field
          name="area"
          v-model="area.name"
          v-bind:label="t('places.area.name')"
          :disabled="formDisabled"
        ></v-text-field>

        <v-row>
          <v-col>
            <v-autocomplete
              name="country_code"
              v-model="area.country_code"
              v-bind:label="t('places.address.country')"
              :disabled="formDisabled"
              :items="dropdownList"
            ></v-autocomplete>
          </v-col>
        </v-row>
      </v-col>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn
        variant="text"
        color="secondary"
        @click="cancelAreaForm"
        :disabled="formDisabled"
        >{{ t("actions.cancel") }}</v-btn
      >
      <v-btn
        variant="elevated"
        color="primary"
        @click="saveAreaForm"
        :loading="formDisabled"
        :disabled="formDisabled"
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

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;

const props = defineProps<{
  initialData: Record<string, any>;
  countries?: any[];
}>();

const emit = defineEmits(["cancel", "saved"]);

const area = ref<any>({ id: 0, name: "", country_code: "" });
const formDisabled = ref(false);

const dropdownList = computed(() => {
  if (!props.countries) return [];
  return props.countries.map((element: any) => ({
    title: t(element.name_i18n),
    value: element.code
  }));
});

watch(
  () => props.initialData,
  (areaProp) => {
    area.value = areaProp;
  }
);

function cancelAreaForm() {
  emit("cancel", false);
}

function saveAreaForm() {
  saveArea("saved");
}

function saveArea(emitMessage: string) {
  let areaId = area.value.id;
  let areaData = {
    name: area.value.name,
    country_code: area.value.country_code
  };
  if (areaId) {
    updateArea(areaData, areaId, emitMessage);
  } else {
    addArea(areaData, emitMessage);
  }
}

function addArea(areaData: any, emitMessage: string) {
  http
    .post("/api/v1/places/areas", areaData)
    .then(resp => {
      emit(emitMessage, resp.data);
      console.log(areaData);
    })
    .then(() => {
      formDisabled.value = false;
      cancelAreaForm();
    })
    .catch(err => {
      console.log("FAILED", err);
      formDisabled.value = false;
    });
}

function updateArea(areaData: any, areaId: number, emitMessage: string) {
  console.log(areaData);
  console.log(areaId);
  http
    .put(`/api/v1/places/areas/${areaId}`, areaData)
    .then(resp => {
      emit(emitMessage, resp.data);
    })
    .then(() => {
      formDisabled.value = false;
      cancelAreaForm();
    })
    .catch(err => {
      console.log("FAILED", err);
      formDisabled.value = false;
    });
}
</script>
