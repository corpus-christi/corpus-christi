<template>
  <v-card>
    <v-card-text>
      <span class="heading">{{ t("places.create-address") }}</span>
      <v-col>
        <v-text-field
          name="address"
          v-model="address.address"
          v-bind:label="t('places.address.address') + ' *'"
          clearable
          :disabled="formDisabled"
        ></v-text-field>

        <v-row>
          <v-col>
            <v-text-field
              name="city"
              v-model="address.city"
              v-bind:label="t('places.address.city') + ' *'"
              v-bind:readonly="formDisabled"
            ></v-text-field>
          </v-col>

          <v-col shrink>
            <v-btn
              variant="text"
              icon
              @click="queryAddress('address')"
              v-bind:disabled="formDisabled"
            >
              <v-icon>search</v-icon>
            </v-btn>
          </v-col>
        </v-row>

        <v-row>
          <v-col>
            <div>
              <v-autocomplete
                name="area"
                hide-details
                solo
                single-line
                :label="t('places.area.area') + ' *'"
                :items="dropdownList"
                v-model="selectedArea"
                :disabled="formDisabled"
              ></v-autocomplete>
            </div>
          </v-col>

          <v-col shrink>
            <v-btn variant="text" icon :disabled="formDisabled" @click="openAreaSubForm">
              <v-icon>add</v-icon>
            </v-btn>
          </v-col>
          <v-dialog
            scrollable
            persistent
            v-model="areaDialog.show"
            max-width="1000px"
          >
            <v-col>
              <v-card>
                <v-row align="center" justify="center">
                  <v-card-title class="headline">
                    {{ t(areaDialog.title) }}
                  </v-card-title>
                </v-row>
              </v-card>
              <AreaForm
                v-on:cancel="cancelArea"
                v-on:saved="refreshPlacesList"
                v-bind:countries="countries"
                v-bind:initialData="areaDialog.area"
              />
            </v-col>
          </v-dialog>
        </v-row>

        <v-text-field
          name="name"
          v-model="address.name"
          v-bind:label="t('places.address.name') + ' *'"
          :readonly="formDisabled"
        ></v-text-field>

        <span body-2 v-if="addressErr" class="red--text">
          {{ t("places.messages.no-results") }}
        </span>
        <gmap-map
          ref="map"
          v-bind:center="center"
          v-bind:zoom="10"
          style="width:400px;  height: 250px;"
          data-cy="gmap"
          @click="markLocation"
          :disabled="formDisabled"
        >
          <gmap-marker :position="marker"></gmap-marker>
        </gmap-map>

        <v-checkbox
          name="toggleAddressMode"
          :label="t('places.address.valid-address')"
          v-model="addressValid"
          :disabled="formDisabled"
        ></v-checkbox>

        <v-checkbox
          name="toggleCheckbox"
          :label="t('places.address.find-address-lat-lng')"
          v-model="latLng"
          :disabled="formDisabled"
        >
        </v-checkbox>

        <span body-2 v-if="findAddressLatLngErr && latLng" class="red--text">
          {{ t("places.messages.find-address-err") }}
        </span>

        <v-text-field
          name="latitude"
          v-model="address.latitude"
          v-show="latLng"
          v-bind:label="t('places.address.latitude')"
        ></v-text-field>

        <v-text-field
          name="longitude"
          v-model="address.longitude"
          v-show="latLng"
          v-bind:label="t('places.address.longitude')"
        ></v-text-field>

        <span body-2 v-if="latLngErr" class="red--text">
          {{ t("places.messages.lat-lng-err") }}
        </span>

        <v-btn
          variant="text"
          color="primary"
          @click="findAddressLatLng"
          :loading="formDisabled"
          :disabled="formDisabled"
          v-show="latLng"
          >{{ t("places.address.find-address") }}</v-btn
        >
      </v-col>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn
        variant="text"
        color="secondary"
        @click="cancelAddressForm"
        :disabled="formDisabled"
        >{{ t("actions.cancel") }}</v-btn
      >
      <v-btn
        variant="elevated"
        color="primary"
        @click="saveAddressForm"
        :loading="formDisabled"
        :disabled="formDisabled || disableSave"
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
import AreaForm from "./AreaForm.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;

const props = defineProps<{
  initialData: Record<string, any>;
  areas?: any[];
  countries?: any[];
}>();

const emit = defineEmits(["cancel", "saved", "subFormSaved"]);

const map = ref<any>(null);
const selectedArea = ref(0);
const address = ref<any>({
  id: 0,
  name: "",
  address: "",
  city: "",
  latitude: "",
  longitude: "",
  country_code: "",
  area_id: ""
});

const areaDialog = ref({
  title: "",
  show: false,
  editMode: false,
  saveLoading: false,
  addMoreLoading: false,
  area: {} as any
});

const center = ref({ lat: -2.90548355117024, lng: -79.02949294174876 });
const marker = ref({ lat: 0, lng: 0 });
const addressErr = ref(false);
const findAddressErr = ref(false);
const findAddressLatLngErr = ref(false);
const latLngErr = ref(false);
const showPlacePicker = ref(false);
const formDisabled = ref(false);
const latLng = ref(false);
const addressValid = ref(true);

const dropdownList = computed(() => {
  if (!props.areas) return [];
  return props.areas.map((element: any) => ({
    title: element.name,
    value: element.id
  }));
});

const disableSave = computed(() => {
  return (
    address.value.address === "" ||
    address.value.city === "" ||
    selectedArea.value === 0 ||
    address.value.name === ""
  );
});

watch(
  () => props.initialData,
  (placeProp) => {
    console.log("DATA BEING PASSED TO ADDRESS FORM");
    console.log(placeProp);
    if (isEmpty(placeProp)) {
      // reset
    } else {
      address.value = placeProp;
      if (placeProp.area_id > 0) {
        selectedArea.value = placeProp.area_id;
      }
    }
  }
);

function resetForm() {
  selectedArea.value = 0;
  address.value.id = 0;
  address.value.name = "";
  address.value.address = "";
  address.value.city = "";
  address.value.latitude = "";
  address.value.longitude = "";
  address.value.country_code = "";
  address.value.area_id = "";
  center.value = { lat: -2.90548355117024, lng: -79.02949294174876 };
  marker.value = { lat: 0, lng: 0 };
  addressErr.value = false;
  showPlacePicker.value = false;
  formDisabled.value = false;
  latLng.value = false;
  findAddressErr.value = false;
  findAddressLatLngErr.value = false;
  latLngErr.value = false;
}

function openAreaSubForm() {
  activateAreaDialog();
}

function activateAreaDialog(area: any = {}, editMode = false) {
  areaDialog.value.title = editMode
    ? t("places.area.edit")
    : t("places.area.new");
  areaDialog.value.area = {
    id: area.id,
    name: area.name,
    country_code: area.country_code
  };
  areaDialog.value.show = true;
}

function cancelArea() {
  areaDialog.value.show = false;
}

function refreshPlacesList() {
  emit("subFormSaved");
}

function cancelAddressForm() {
  resetForm();
  emit("cancel", false);
}

async function saveAddressForm() {
  formDisabled.value = true;
  if (address.value.latitude === "" || address.value.longitude === "") {
    await queryAddress("address");
  }
  let addressId = address.value.id;
  let addressData = {
    name: address.value.name,
    address: address.value.address,
    city: address.value.city,
    latitude: address.value.latitude,
    longitude: address.value.longitude,
    country_code: address.value.country_code,
    area_id: selectedArea.value
  };
  if (addressId) {
    updateAddress(addressData, addressId, "saved");
  } else {
    addAddress(addressData, "saved");
  }
}

function addAddress(addressData: any, emitMessage: string) {
  http
    .post("/api/v1/places/addresses", addressData)
    .then(resp => {
      emit(emitMessage, resp.data);
    })
    .then(() => {
      formDisabled.value = false;
      cancelAddressForm();
    })
    .catch(err => {
      console.log("FAILED", err);
      formDisabled.value = false;
    });
}

function updateAddress(addressData: any, addressId: number, emitMessage: string) {
  http
    .put(`/api/v1/places/addresses/${addressId}`, addressData)
    .then(resp => {
      emit(emitMessage, resp.data);
    })
    .then(() => {
      formDisabled.value = false;
      cancelAddressForm();
    })
    .catch(err => {
      console.log("FAILED", err);
      formDisabled.value = false;
    });
}

function findAddressLatLng() {
  address.value.city = "";
  queryAddress("lat-lng");
}

async function queryAddress(type: string) {
  if (latLng.value) {
    if (address.value.latitude === "" || address.value.longitude === "") {
      findAddressLatLngErr.value = true;
      return;
    } else {
      findAddressLatLngErr.value = false;
    }
  }
  return new Promise<void>((resolve, reject) => {
    // Geocoder integration would go here
    resolve();
  });
}

function markLocation(location: any) {
  address.value.address = "Selected Address";
  address.value.city = "Selected City";
  address.value.latitude = location.latLng.lat();
  address.value.longitude = location.latLng.lng();
  marker.value = location.latLng;
  centerMapOnMarker();
  if (addressValid.value) {
    queryAddress("lat-lng");
  } else {
    queryAddress("address");
  }
}

function centerMapOnMarker() {
  if (map.value) {
    map.value.panTo(marker.value);
  }
}

onMounted(() => {
  if (map.value && map.value.$mapPromise) {
    map.value.$mapPromise.then((m: any) => {
      map.value = m;
    });
  }
});
</script>
