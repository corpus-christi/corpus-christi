<template>
  <v-card>
    <v-card-text>
      <span class="headling">{{ $t("places.create-address") }}</span>
      <v-layout column>
        <v-text-field
          name="address"
          v-model="address.address"
          v-bind:label="$t('places.address.address')"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('address')"
          clearable
          :disabled="formDisabled"
        ></v-text-field>

        <v-layout row>
          <v-flex>
            <v-text-field
              name="city"
              v-model="address.city"
              v-bind:label="$t('places.address.city')"
              v-validate="'required|alpha_spaces'"
              v-bind:error-messages="errors.collect('city')"
              v-bind:readonly="formDisabled"
            ></v-text-field>
          </v-flex>

          <v-flex shrink>
            <v-btn
              flat
              icon
              @click="queryAddress('address')"
              v-bind:disabled="formDisabled"
            >
              <v-icon>search</v-icon>
            </v-btn>
          </v-flex>
        </v-layout>

        <v-layout row>
          <v-flex>
            <!-- <v-text-field
              name="area"
              v-model="address.area_name"
              v-bind:label="$t('places.area')"
              :disabled="formDisabled"
            ></v-text-field>-->
            <div>
              <v-select
                name="area"
                hide-details
                solo
                single-line
                :label="$t('places.area')"
                :items="dropdownList"
                v-model="selectedArea"
                v-validate="'required'"
                :error-messages="errors.collect('area')"
                :disabled="formDisabled"
              ></v-select>
            </div>
          </v-flex>

          <v-flex shrink>
            <v-btn flat icon :disabled="formDisabled">
              <v-icon>search</v-icon>
            </v-btn>
          </v-flex>
        </v-layout>

        <span body-2 v-if="addressErr" class="red--text">
          {{ $t("places.messages.no-results") }}
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
          name="toggleCheckbox"
          label="Show Latitude and Longitude"
          v-on:change="toggleLatLng"
          :disabled="formDisabled"
        >
        </v-checkbox>
        <v-text-field
          name="name"
          v-model="address.name"
          v-bind:label="$t('places.address.name')"
          v-validate="'required'"
          :error-messages="errors.collect('name')"
          :readonly="formDisabled"
        ></v-text-field>

        <v-text-field
          name="latitude"
          v-model="address.latitude"
          v-show="latLng"
          v-bind:label="$t('places.address.latitude')"
          :disabled="formDisabled"
        ></v-text-field>

        <v-text-field
          name="longitude"
          v-model="address.longitude"
          v-show="latLng"
          v-bind:label="$t('places.address.longitude')"
          :disabled="formDisabled"
        ></v-text-field>
      </v-layout>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn
        flat
        color="secondary"
        @click="cancelAddressForm"
        :disabled="formDisabled"
        >{{ $t("actions.cancel") }}</v-btn
      >
      <v-btn
        raised
        color="primary"
        @click="saveAddressForm"
        :loading="formDisabled"
        :disabled="formDisabled"
        >{{ $t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script>
import { isEmpty } from "lodash";

export default {
  name: "PlaceForm",
  props: {
    initialData: {
      type: Object,
      required: true
    },
    areas: {
      type: Array
    }
  },
  data: function() {
    return {
      selectedArea: 0,
      address: {
        id: 0,
        name: "",
        address: "",
        city: "",
        latitude: "",
        longitude: "",
        country_code: "",
        area_id: ""
      },
      center: { lat: -2.90548355117024, lng: -79.02949294174876 },
      marker: { lat: 0, lng: 0 },
      map: null,
      addressErr: false,
      showPlacePicker: false,
      formDisabled: false,
      latLng: false
    };
  },
  computed: {
    showLatLng: function() {
      return this.latLng;
    },
    dropdownList() {
      return this.areas.map(element => {
        return {
          text: element.name,
          value: element.id
        };
      });
    }
  },
  watch: {
    // Make sure data stays in sync with any changes to `initialData` from parent.
    initialData(placeProp) {
      console.log("DATA BEING PASSED TO ADDRESS FORM");
      console.log(placeProp);
      if (isEmpty(placeProp)) {
        this.$validator.reset();
      } else {
        this.address = placeProp;
        if (placeProp.area_id > 0) {
          this.selectedArea = placeProp.area_id;
        }
      }
    }
  },
  methods: {
    resetForm() {
      // reset address values back to defaults
      this.selectedArea = 0;
      this.address.id = 0;
      this.address.name = "";
      this.address.address = "";
      this.address.city = "";
      this.address.latitude = "";
      this.address.longitude = "";
      this.address.country_code = "";
      this.address.area_id = "";
      this.center = { lat: -2.90548355117024, lng: -79.02949294174876 };
      this.marker = { lat: 0, lng: 0 };
      this.map = null;
      this.addressErr = false;
      this.showPlacePicker = false;
      this.formDisabled = false;
      this.latLng = false;
    },
    cancelAddressForm() {
      // emit false to close form
      this.resetForm();
      this.$validator.reset();
      this.$emit("cancel", false);
    },
    toggleLatLng() {
      this.latLng = !this.latLng;
    },
    saveAddressForm() {
      this.saveAddress("saved");
    },
    saveAddress(emitMessage) {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          let addressId = this.address.id;
          let addressData = {
            name: this.address.name,
            address: this.address.address,
            city: this.address.city,
            latitude: this.address.latitude,
            longitude: this.address.longitude,
            country_code: this.address.country_code,
            area_id: this.selectedArea
          };
          if (addressId) {
            this.updateAddress(addressData, addressId, emitMessage);
          } else {
            this.addAddress(addressData, emitMessage);
          }
        } else {
          console.log("there were errors");
        }
      });
    },
    addAddress(addressData, emitMessage) {
      this.$http
        .post("/api/v1/places/addresses", addressData)
        .then(resp => {
          this.$emit(emitMessage, resp.data);
        })
        .then(() => {
          this.formDisabled = false;
          this.cancelAddressForm();
        })
        .catch(err => {
          console.log("FAILED", err);
          this.formDisabled = false;
        });
    },
    updateAddress(addressData, addressId, emitMessage) {
      this.$http
        .put(`/api/v1/places/addresses/${addressId}`, addressData)
        .then(resp => {
          this.$emit(emitMessage, resp.data);
        })
        .then(() => {
          this.formDisabled = false;
          this.cancelAddressForm();
        })
        .catch(err => {
          console.log("FAILED", err);
          this.formDisabled = false;
        });
    },
    async queryAddress(type) {
      const isValid = await this.$validator.validateAll();
      if (!isValid) {
        return;
      } else {
        return new Promise((resolve, reject) => {
          this.$geocoder.setDefaultMode(type);

          var addressObj;
          if (type === "address") {
            addressObj = {
              address_line_1: this.address.address,
              city: this.address.city
            };
          } else if (type === "lat-lng") {
            addressObj = {
              lat: this.address.latitude,
              lng: this.address.longitude
            };
          } else {
            return;
          }

          try {
            this.$geocoder.send(addressObj, response => {
              if (response.status === "ZERO_RESULTS") {
                this.addressErr = true;
                return;
              } else {
                this.addressErr = false;
                let addr = response.results[0];
                this.address.address = addr.formatted_address;
                this.address.latitude = addr.geometry.location.lat;
                this.address.longitude = addr.geometry.location.lng;
                let addrcomps = addr.address_components;
                for (let comp of addrcomps) {
                  for (type of comp.types) {
                    if (type === "country") {
                      this.address.country_code = comp.short_name;
                      this.address.area_name = comp.long_name;
                    } else if (type === "locality") {
                      this.address.city = comp.long_name;
                    } else if (
                      type === "administrative_area_level_1" ||
                      type === "administrative_area_level_2"
                    ) {
                      this.address.area_name = comp.long_name;
                    }
                  }
                }
                this.marker = {
                  lat: this.address.latitude,
                  lng: this.address.longitude
                };
                this.centerMapOnMarker();
                resolve();
              }
            });
          } catch (err) {
            console.log(err);
            reject(err);
          }
        });
      }
    },

    markLocation(location) {
      this.address.address = "Selected Address";
      this.address.city = "Selected City";
      this.address.latitude = location.latLng.lat();
      this.address.longitude = location.latLng.lng();
      this.marker = location.latLng;
      this.centerMapOnMarker();

      this.queryAddress("lat-lng");
    },

    centerMapOnMarker() {
      this.map.panTo(this.marker);
    }
  },

  mounted: function() {
    this.$refs.map.$mapPromise.then(m => {
      this.map = m;
    });
  }
};
</script>
