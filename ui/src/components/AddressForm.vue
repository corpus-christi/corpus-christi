<template>
  <v-card>
    <v-card-text>
      <span class="headling"> {{ title }} </span>
      <v-layout column>
        <v-text-field
          name="address"
          v-model="address.address"
          v-bind:label="$t('places.address.address')"
          v-validate="'required'"
          :error-messages="errors.collect('address')"
          clearable
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
            ></v-text-field>
          </v-flex>

          <v-flex shrink>
            <v-btn flat icon @click="queryAddress('address')"
              ><v-icon>search</v-icon></v-btn
            >
          </v-flex>
        </v-layout>

        <span body-2 v-if="addressErr" class="red--text"
          >Your address returned no results.</span
        >
        <gmap-map
          ref="map"
          v-bind:center="center"
          v-bind:zoom="10"
          style="width:400px;  height: 250px;"
          data-cy="gmap"
          @click="markLocation"
        >
          <gmap-marker :position="marker"></gmap-marker>
        </gmap-map>

        <v-text-field
          name="name"
          v-model="address.name"
          v-bind:label="$t('places.address.name')"
        ></v-text-field>

        <v-textarea
          name="description"
          v-model="address.description"
          v-bind:label="$t('places.location.description')"
        ></v-textarea>
      </v-layout>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn flat color="secondary" @click="closeAddressForm">Cancel</v-btn>
      <v-btn raised color="primary">Save</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  name: "AddressForm",
  props: {
    title: {
      type: String,
      required: false,
      default: "Create an Address"
    }
  },
  data: function() {
    return {
      address: {
        name: "",
        description: "",
        address: "",
        city: "",
        latitude: "",
        longitude: ""
      },
      center: { lat: -2.90548355117024, lng: -79.02949294174876 },
      marker: { lat: 0, lng: 0 },
      map: null,
      addressErr: false,
      showPlacePicker: false
    };
  },
  methods: {
    closeAddressForm() {
      // emit false to close form
      this.$emit("cancel", false);
    },

    async queryAddress(type) {
      const isValid = await this.$validator.validateAll();
      if (!isValid) {
        return;
      } else {
        this.$geocoder.setDefaultMode(type);

        // Av. Felipe II y Circunvalación Sur, Ave Circunvalación Sur, Cuenca
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
              this.marker = {
                lat: this.address.latitude,
                lng: this.address.longitude
              };
              this.centerMapOnMarker();
            }
          });
        } catch (err) {
          console.log(err);
        }
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
