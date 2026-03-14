<template>
  <v-card>
    <v-card-text>
      <span class="heading" v-if="locationInfo.editMode">{{
        t("places.location.location")
      }}</span>
      <span class="heading" v-else>{{ t("places.location.new") }}</span>
      <v-col>
        <div>
          <v-autocomplete
            v-if="locationInfo.editMode"
            name="area"
            hide-details
            solo
            single-line
            :label="t('places.location.location')"
            :items="dropDownList"
            v-model="selectedLocation"
            :disabled="formDisabled"
            v-on:update:model-value="updateDescription(); isDisabled();"
          />
        </div>
      </v-col>
      <v-text-field
        name="description"
        v-bind:label="t('places.location.description')"
        v-model="location.description"
        clearable
        :disabled="formDisabled"
      ></v-text-field>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn
        variant="text"
        color="secondary"
        @click="cancelLocationForm"
        :disabled="formDisabled"
        >{{ t("actions.cancel") }}</v-btn
      >
      <v-btn
        variant="elevated"
        color="primary"
        @click="saveLocationForm"
        :loading="formDisabled"
        :disabled="subDisabled"
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
}>();

const emit = defineEmits(["cancel", "saved"]);

const selectedLocation = ref(0);
const locationInfo = ref<any>({
  address_id: 0,
  allLocations: [],
  editMode: false
});
const location = ref<any>({ id: 0, description: "", address_id: 0 });
const formDisabled = ref(false);
const subDisabled = ref(false);

const dropDownList = computed(() => {
  return locationInfo.value.allLocations.map((element: any) => ({
    title: t(element.description),
    value: element.id
  }));
});

watch(
  () => props.initialData,
  (locationProp) => {
    locationInfo.value = locationProp;
    selectedLocation.value = 0;
    subDisabled.value =
      formDisabled.value || !(!locationInfo.value.editMode || selectedLocation.value);
  }
);

function isDisabled() {
  subDisabled.value =
    formDisabled.value || !(!locationInfo.value.editMode || selectedLocation.value);
}

function updateDescription() {
  for (let i = 0; i < locationInfo.value.allLocations.length; i++) {
    if (locationInfo.value.allLocations[i].id === selectedLocation.value) {
      location.value.description = locationInfo.value.allLocations[i].description;
    }
  }
}

function cancelLocationForm() {
  location.value.description = "";
  selectedLocation.value = 0;
  emit("cancel", false);
}

function saveLocationForm() {
  saveLocation("saved");
}

function saveLocation(emitMessage: string) {
  let locationId = selectedLocation.value;
  let locationData = {
    description: location.value.description,
    address_id: locationInfo.value.address_id
  };
  if (locationId) {
    updateLocation(locationData, locationId, emitMessage);
  } else {
    addLocation(locationData, emitMessage);
  }
  selectedLocation.value = 0;
}

function addLocation(locationData: any, emitMessage: string) {
  http
    .post("/api/v1/places/locations", locationData)
    .then(resp => {
      emit(emitMessage, resp.data);
    })
    .then(() => {
      formDisabled.value = false;
      cancelLocationForm();
    })
    .catch(err => {
      console.log("FAILED", err);
      formDisabled.value = false;
    });
}

function updateLocation(locationData: any, locationId: number, emitMessage: string) {
  http
    .put(`api/v1/places/locations/${locationId}`, locationData)
    .then(resp => {
      emit(emitMessage, resp.data);
    })
    .then(() => {
      formDisabled.value = false;
      cancelLocationForm();
    })
    .catch(err => {
      console.log("FAILED", err);
      formDisabled.value = false;
    });
}
</script>
