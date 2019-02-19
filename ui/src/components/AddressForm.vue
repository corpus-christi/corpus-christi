<template>
  <v-card>
    <v-card-text>
      <span class="headling">{{ title }}</span>
      <v-layout column>
        <v-text-field
          name="address"
          v-model="address.address"
          v-bind:label="$t('places.address.address')"
          v-validate="'required'"
          :error-messages="errors.collect('address')"
          clearable
          :disabled="formDisabled"
        ></v-text-field>

        <v-layout row>
          <v-flex>
            <v-text-field
              slot="activator"
              name="city"
              v-model="address.city"
              v-bind:label="$t('places.address.city')"
              v-validate="'required'"
              :error-messages="errors.collect('city')"
              clearable
              :disabled="formDisabled"
            ></v-text-field>
          </v-flex>

          <v-flex shrink>
            <v-btn
              flat
              icon
              @click="queryAddress('address')"
              :disabled="formDisabled"
            >
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

        <v-text-field
          name="name"
          v-model="address.address_name"
          v-bind:label="$t('places.address.name')"
          :disabled="formDisabled"
        ></v-text-field>

        <v-textarea
          name="description"
          v-model="address.description"
          v-bind:label="$t('places.location.description')"
          :disabled="formDisabled"
        ></v-textarea>
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
export default {
  name: "AddressForm",
  data: function() {
    return {
      address: {
        address_name: "",
        description: "",
        address: "",
        city: "",
        latitude: "",
        longitude: "",
        country_code: "",
        area_name: ""
      },
      center: { lat: -2.90548355117024, lng: -79.02949294174876 },
      marker: { lat: 0, lng: 0 },
      map: null,
      addressErr: false,
      showPlacePicker: false,
      formDisabled: false,
      title: this.$t("places.create-address")
    };
  },
  methods: {
    cancelAddressForm() {
      // emit false to close form
      this.$emit("cancel", false);
    },

    async saveAddressForm() {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          this.formDisabled = true;
          if (this.address.latitude === "" || this.address.longitude === "") {
            this.queryAddress("address").then(() => {
              this.sendData();
            });
          } else {
            this.sendData();
          }
        }
      });
    },

    sendData() {
      this.$http
        .post("/api/v1/places/locations", this.address)
        .then(resp => {
          this.$emit("saved", resp.data);
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
