<template>
  <v-card>
    <v-card-text>
      <span class="headling">{{ title }}</span>
      <v-row>
        <v-col cols="12">
          <v-text-field
            name="address"
            v-model="address.address"
            v-bind:label="t('places.address.address')"
            :error-messages="addressErrors"
            clearable
            :disabled="formDisabled"
          ></v-text-field>
        </v-col>

        <v-col cols="12">
          <v-row>
            <v-col>
              <v-text-field
                name="city"
                v-model="address.city"
                v-bind:label="t('places.address.city')"
                :error-messages="cityErrors"
                clearable
                :disabled="formDisabled"
              ></v-text-field>
            </v-col>

            <v-col cols="auto">
              <v-btn
                variant="text"
                icon
                @click="queryAddress('address')"
                :disabled="formDisabled"
              >
                <v-icon>search</v-icon>
              </v-btn>
            </v-col>
          </v-row>
        </v-col>

        <v-col cols="12">
          <span body-2 v-if="addressErr" class="red--text">
            {{ t("places.messages.no-results") }}
          </span>
          <GmapMap
            ref="mapRef"
            v-bind:center="center"
            v-bind:zoom="10"
            style="width:400px;  height: 250px;"
            data-cy="gmap"
            @click="markLocation"
            :disabled="formDisabled"
          >
            <GmapMarker :position="marker"></GmapMarker>
          </GmapMap>
        </v-col>

        <v-col cols="12">
          <v-text-field
            name="name"
            v-model="address.address_name"
            v-bind:label="t('places.address.name')"
            :disabled="formDisabled"
          ></v-text-field>
        </v-col>

        <v-col cols="12">
          <v-textarea
            name="description"
            v-model="address.description"
            v-bind:label="t('places.location.description')"
            :disabled="formDisabled"
          ></v-textarea>
        </v-col>
      </v-row>
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
        color="primary"
        @click="saveAddressForm"
        :loading="formDisabled"
        :disabled="formDisabled"
        >{{ t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;

const emit = defineEmits(["cancel", "saved"]);

const address = ref({
  address_name: "",
  description: "",
  address: "",
  city: "",
  latitude: "" as string | number,
  longitude: "" as string | number,
  country_code: "",
  area_name: ""
});
const center = ref({ lat: -2.90548355117024, lng: -79.02949294174876 });
const marker = ref({ lat: 0, lng: 0 });
const map = ref<any>(null);
const addressErr = ref(false);
const formDisabled = ref(false);
const title = t("places.create-address");
const mapRef = ref<any>(null);

const addressErrors = ref<string[]>([]);
const cityErrors = ref<string[]>([]);

function validateForm(): boolean {
  addressErrors.value = [];
  cityErrors.value = [];
  let valid = true;
  if (!address.value.address) {
    addressErrors.value = [t("validations.required")];
    valid = false;
  }
  if (!address.value.city) {
    cityErrors.value = [t("validations.required")];
    valid = false;
  }
  return valid;
}

function cancelAddressForm() {
  emit("cancel", false);
}

async function saveAddressForm() {
  if (!validateForm()) return;
  formDisabled.value = true;
  if (address.value.latitude === "" || address.value.longitude === "") {
    queryAddress("address").then(() => {
      sendData();
    });
  } else {
    sendData();
  }
}

function sendData() {
  http
    .post("/api/v1/places/locations", address.value)
    .then(resp => {
      emit("saved", resp.data);
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

function geocode(type: string, addressObj: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const geocoder = new (window as any).google.maps.Geocoder();
    let request: any;
    if (type === "address") {
      request = { address: addressObj.address_line_1 + ", " + addressObj.city };
    } else if (type === "lat-lng") {
      request = { location: { lat: addressObj.lat, lng: addressObj.lng } };
    } else {
      reject(new Error("Unknown geocode type"));
      return;
    }
    geocoder.geocode(request, (results: any[], status: string) => {
      resolve({ results, status });
    });
  });
}

async function queryAddress(type: string): Promise<void> {
  if (!validateForm()) return;

  let addressObj: any;
  if (type === "address") {
    addressObj = {
      address_line_1: address.value.address,
      city: address.value.city
    };
  } else if (type === "lat-lng") {
    addressObj = {
      lat: address.value.latitude,
      lng: address.value.longitude
    };
  } else {
    return;
  }

  try {
    const response = await geocode(type, addressObj);
    if (response.status === "ZERO_RESULTS") {
      addressErr.value = true;
      return;
    } else {
      addressErr.value = false;
      let addr = response.results[0];
      address.value.address = addr.formatted_address;
      address.value.latitude = addr.geometry.location.lat();
      address.value.longitude = addr.geometry.location.lng();
      let addrcomps = addr.address_components;
      for (let comp of addrcomps) {
        for (let compType of comp.types) {
          if (compType === "country") {
            address.value.country_code = comp.short_name;
            address.value.area_name = comp.long_name;
          } else if (compType === "locality") {
            address.value.city = comp.long_name;
          } else if (
            compType === "administrative_area_level_1" ||
            compType === "administrative_area_level_2"
          ) {
            address.value.area_name = comp.long_name;
          }
        }
      }
      marker.value = {
        lat: address.value.latitude as number,
        lng: address.value.longitude as number
      };
      centerMapOnMarker();
    }
  } catch (err) {
    console.log(err);
  }
}

function markLocation(location: any) {
  address.value.address = "Selected Address";
  address.value.city = "Selected City";
  address.value.latitude = location.latLng.lat();
  address.value.longitude = location.latLng.lng();
  marker.value = { lat: location.latLng.lat(), lng: location.latLng.lng() };
  centerMapOnMarker();
  queryAddress("lat-lng");
}

function centerMapOnMarker() {
  if (map.value) {
    map.value.panTo(marker.value);
  }
}

onMounted(() => {
  if (mapRef.value) {
    mapRef.value.$mapPromise.then((m: any) => {
      map.value = m;
    });
  }
});
</script>
