<template>
  <v-card>
    <v-card-text>
      <span class="heading">{{ $t("places.create-address") }}</span>
      <v-layout column>
        <v-text-field
          name="address"
          v-model="address.address"
          v-bind:label="$t('places.address.address') + ' *'"
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
              v-bind:label="$t('places.address.city') + ' *'"
              v-validate="'required|alpha_spaces'"
              v-bind:error-messages="errors.collect('city')"
              v-bind:readonly="formDisabled"
            ></v-text-field>
          </v-flex>

          <v-flex shrink>
            <v-btn
              text
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
            <div>
              <v-autocomplete
                v-bind:countries="countries"
                name="area"
                hide-details
                solo
                single-line
                :label="$t('places.area.area') + ' *'"
                :items="dropdownList"
                v-model="selectedArea"
                v-validate="'required'"
                :error-messages="errors.collect('area')"
                :disabled="formDisabled"
              ></v-autocomplete>
            </div>
          </v-flex>

          <v-flex shrink>
            <v-btn text icon :disabled="formDisabled" @click="openAreaSubForm">
              <v-icon>add</v-icon>
            </v-btn>
          </v-flex>
          <v-dialog
            scrollable
            persistent
            v-model="areaDialog.show"
            max-width="1000px"
          >
            <v-layout column>
              <v-card>
                <v-layout align-center justify-center row fill-height>
                  <v-card-title class="headline">
                    {{ $t(areaDialog.title) }}
                  </v-card-title>
                </v-layout>
              </v-card>
              <AreaForm
                v-on:cancel="cancelArea"
                v-on:saved="refreshPlacesList"
                v-bind:countries="countries"
                v-bind:initialData="areaDialog.area"
              />
            </v-layout>
          </v-dialog>
        </v-layout>

        <v-text-field
          name="name"
          v-model="address.name"
          v-bind:label="$t('places.address.name') + ' *'"
          :readonly="formDisabled"
        ></v-text-field>

        <span body-2 v-if="addressErr" class="red--text">
          {{ $t("places.messages.no-results") }}
        </span>
        <gmap-map
          ref="map"
          v-bind:center="center"
          v-bind:zoom="10"
          style="width: 400px; height: 250px;"
          data-cy="gmap"
          @click="markLocation"
          :disabled="formDisabled"
        >
          <gmap-marker :position="marker"></gmap-marker>
        </gmap-map>

        <v-checkbox
          name="toggleAddressMode"
          :label="$t('places.address.valid-address')"
          v-model="addressValid"
          :disabled="formDisabled"
        ></v-checkbox>

        <v-checkbox
          name="toggleCheckbox"
          :label="$t('places.address.find-address-lat-lng')"
          v-model="latLng"
          :disabled="formDisabled"
        >
        </v-checkbox>

        <span body-2 v-if="findAddressLatLngErr && latLng" class="red--text">
          {{ $t("places.messages.find-address-err") }}
        </span>

        <v-text-field
          name="latitude"
          v-model="address.latitude"
          v-show="latLng"
          v-bind:label="$t('places.address.latitude')"
        ></v-text-field>

        <v-text-field
          name="longitude"
          v-model="address.longitude"
          v-show="latLng"
          v-bind:label="$t('places.address.longitude')"
        ></v-text-field>

        <span body-2 v-if="latLngErr" class="red--text">
          {{ $t("places.messages.lat-lng-err") }}
        </span>

        <v-btn
          text
          color="primary"
          @click="findAddressLatLng"
          :loading="formDisabled"
          :disabled="formDisabled"
          v-show="latLng"
          >{{ $t("places.address.find-address") }}</v-btn
        >
      </v-layout>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn
        text
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
        :disabled="formDisabled || disableSave"
        >{{ $t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script>
import { isEmpty } from "lodash";
import AreaForm from "./AreaForm";

export default {
  name: "PlaceForm",
  components: { AreaForm },
  props: {
    initialData: {
      type: Object,
      required: true,
    },
    areas: {
      type: Array,
    },
    countries: {
      type: Array,
    },
  },
  data: function () {
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
        area_id: "",
      },
      areaDialog: {
        title: "",
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        area: {},
      },
      center: { lat: -2.90548355117024, lng: -79.02949294174876 },
      marker: { lat: 0, lng: 0 },
      map: null,
      addressErr: false,
      findAddressErr: false,
      findAddressLatLngErr: false,
      latLngErr: false,
      showPlacePicker: false,
      formDisabled: false,
      latLng: false,
      addressValid: true,
    };
  },
  computed: {
    dropdownList() {
      return this.areas.map((element) => {
        return {
          text: element.name,
          value: element.id,
        };
      });
    },
    disableSave() {
      return (
        this.address.address === "" ||
        this.address.city === "" ||
        this.selectedArea === 0 ||
        this.address.name === ""
      );
    },
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
    },
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
      this.addressErr = false;
      this.showPlacePicker = false;
      this.formDisabled = false;
      this.latLng = false;
      this.findAddressErr = false;
      this.findAddressLatLngErr = false;
      this.latLngErr = false;
    },
    openAreaSubForm() {
      this.activateAreaDialog();
    },
    activateAreaDialog(area = {}, editMode = false) {
      this.areaDialog.title = editMode
        ? this.$t("places.area.edit")
        : this.$t("places.area.new");
      this.areaDialog.area = {
        id: area.id,
        name: area.name,
        country_code: area.country_code,
      };
      this.areaDialog.show = true;
    },
    cancelArea() {
      this.areaDialog.show = false;
    },
    refreshPlacesList() {
      this.$emit("subFormSaved");
    },
    cancelAddressForm() {
      // emit false to close form
      this.resetForm();
      this.$validator.reset();
      this.$emit("cancel", false);
    },
    async saveAddressForm() {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          this.formDisabled = true;
          if (this.address.latitude === "" || this.address.longitude === "") {
            this.queryAddress("address").then(() => {
              let addressId = this.address.id;
              let addressData = {
                name: this.address.name,
                address: this.address.address,
                city: this.address.city,
                latitude: this.address.latitude,
                longitude: this.address.longitude,
                country_code: this.address.country_code,
                area_id: this.selectedArea,
              };
              if (addressId) {
                this.updateAddress(addressData, addressId, "saved");
              } else {
                this.addAddress(addressData, "saved");
              }
            });
          } else {
            let addressId = this.address.id;
            let addressData = {
              name: this.address.name,
              address: this.address.address,
              city: this.address.city,
              latitude: this.address.latitude,
              longitude: this.address.longitude,
              country_code: this.address.country_code,
              area_id: this.selectedArea,
            };
            if (addressId) {
              this.updateAddress(addressData, addressId, "saved");
            } else {
              this.addAddress(addressData, "saved");
            }
          }
        }
      });
    },
    addAddress(addressData, emitMessage) {
      this.$http
        .post("/api/v1/places/addresses", addressData)
        .then((resp) => {
          this.$emit(emitMessage, resp.data);
        })
        .then(() => {
          this.formDisabled = false;
          this.cancelAddressForm();
        })
        .catch((err) => {
          console.log("FAILED", err);
          this.formDisabled = false;
        });
    },
    updateAddress(addressData, addressId, emitMessage) {
      this.$http
        .put(`/api/v1/places/addresses/${addressId}`, addressData)
        .then((resp) => {
          this.$emit(emitMessage, resp.data);
        })
        .then(() => {
          this.formDisabled = false;
          this.cancelAddressForm();
        })
        .catch((err) => {
          console.log("FAILED", err);
          this.formDisabled = false;
        });
    },
    findAddressLatLng() {
      this.address.city = "";
      this.queryAddress("lat-lng");
    },
    async queryAddress(type) {
      let isValid;
      if (this.latLng) {
        if (this.address.latitude === "" || this.address.longitude === "") {
          this.findAddressLatLngErr = true;
          isValid = false;
        } else {
          this.findAddressLatLngErr = false;
          isValid = true;
        }
      } else {
        isValid = await this.$validator.validateAll();
      }
      if (!isValid) {
        return;
      } else {
        return new Promise((resolve, reject) => {
          this.$geocoder.setDefaultMode(type);

          var addressObj;
          if (type === "address") {
            addressObj = {
              address_line_1: this.address.address,
              city: this.address.city,
            };
          } else if (type === "lat-lng") {
            addressObj = {
              lat: this.address.latitude,
              lng: this.address.longitude,
            };
          } else {
            return;
          }
          console.log("ADDRESSOBJ CREATED: ");
          console.log(addressObj);
          try {
            this.$geocoder.send(addressObj, (response) => {
              if (response.status === "ZERO_RESULTS") {
                console.log("NO ADDRESS RESULTS");
                this.addressErr = true;
                return;
              } else {
                this.addressErr = false;
                console.log("RESPONSE: ");
                console.log(response);
                let addr = response.results[0];
                console.log("addr variable: ");
                console.log(addr);
                this.address.address = addr.formatted_address;
                this.address.latitude = addr.geometry.location.lat;
                this.address.longitude = addr.geometry.location.lng;
                let addrcomps = addr.address_components;
                for (let comp of addrcomps) {
                  for (type of comp.types) {
                    if (type === "country") {
                      // look through dropdown for longname in list
                      this.address.country_code = comp.short_name;
                      //this.address.area_name = comp.long_name;
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
                if (this.address.city === "") {
                  this.address.city = "Selected City";
                }
                this.marker = {
                  lat: this.address.latitude,
                  lng: this.address.longitude,
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
      if (this.addressValid) {
        this.queryAddress("lat-lng");
      } else {
        this.queryAddress("address");
      }
    },

    centerMapOnMarker() {
      this.map.panTo(this.marker);
    },
  },

  mounted: function () {
    this.$refs.map.$mapPromise.then((m) => {
      this.map = m;
    });
  },
};
</script>
