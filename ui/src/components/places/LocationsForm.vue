<template>
  <v-card>
    <v-card-text>
      <span class="heading" v-if="this.locationInfo.editMode">{{
        $t("places.location.location")
      }}</span>
      <span class="heading" v-else>{{ $t("places.location.new") }}</span>
      <v-flex>
        <div>
          <v-autocomplete
            v-if="this.locationInfo.editMode"
            name="area"
            hide-details
            solo
            single-line
            :label="$t('places.location.location')"
            :items="dropDownList"
            v-model="selectedLocation"
            v-validate="'required'"
            :error-messages="errors.collect('location')"
            :disabled="formDisabled"
            v-on:change="updateDescription() + isDisabled()"
          ></v-autocomplete>
        </div>
      </v-flex>
      <v-text-field
        name="description"
        v-bind:label="$t('places.location.description')"
        v-model="location.description"
        clearable
        :disabled="formDisabled"
      ></v-text-field>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn
        flat
        color="secondary"
        @click="cancelLocationForm"
        :disabled="formDisabled"
        >{{ $t("actions.cancel") }}</v-btn
      >
      <v-btn
        raised
        color="primary"
        @click="saveLocationForm"
        :loading="formDisabled"
        :disabled="subDisabled"
        >{{ $t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  name: "LocationsForm",
  editMode: false,
  props: {
    initialData: {
      type: Object,
      required: true
    }
  },
  data: function() {
    return {
      selectedLocation: 0,
      locationInfo: {
        address_id: 0,
        allLocations: [],
        editMode: Boolean
      },
      location: {
        id: 0,
        description: "",
        address_id: 0
      },
      formDisabled: false,
      saveIsLoading: false,
      subDisabled: false,
      dropList: {}
    };
  },
  computed: {
    dropDownList() {
      return this.locationInfo.allLocations.map(element => {
        return {
          text: this.$t(element.description),
          value: element.id
        };
      });
    }
  },
  watch: {
    initialData(locationProp) {
      this.locationInfo = locationProp;
      this.subDisabled =
        this.formDisabled || !(!this.editMode || this.selectedLocation);
    }
  },
  methods: {
    isDisabled() {
      this.subDisabled =
        this.formDisabled || !(!this.editMode || this.selectedLocation);
    },
    updateDescription() {
      for (let i = 0; i < this.locationInfo.allLocations.length; i++) {
        if (this.locationInfo.allLocations[i].id === this.selectedLocation) {
          this.location.description = this.locationInfo.allLocations[
            i
          ].description;
        }
      }
    },
    cancelLocationForm() {
      this.location.description = "";
      this.selectedLocation = 0;
      this.$emit("cancel", false);
    },
    saveLocationForm() {
      this.saveLocation("saved");
    },
    saveLocation(emitMessage) {
      let locationId = this.selectedLocation;
      let locationData = {
        description: this.location.description,
        address_id: this.locationInfo.address_id
      };
      if (locationId) {
        this.updateLocation(locationData, locationId, emitMessage);
      } else {
        this.addLocation(locationData, emitMessage);
      }
      this.selectedLocation = 0;
    },
    addLocation(locationData, emitMessage) {
      this.$http
        .post("/api/v1/places/locations", locationData)
        .then(resp => {
          this.$emit(emitMessage, resp.data);
        })
        .then(() => {
          this.formDisabled = false;
          this.cancelLocationForm();
        })
        .catch(err => {
          console.log("FAILED", err);
          this.formDisabled = false;
        });
    },
    updateLocation(locationData, locationId, emitMessage) {
      this.$http
        .put(`api/v1/places/locations/${locationId}`, locationData)
        .then(resp => {
          this.$emit(emitMessage, resp.data);
        })
        .then(() => {
          this.formDisabled = false;
          this.cancelLocationForm();
        })
        .catch(err => {
          console.log("FAILED", err);
          this.formDisabled = false;
        });
    }
  }
};
</script>
