<template>
  <v-container>
    <v-tabs color="transparent" slider-color="accent">
      <v-tab ripple data-cy="places-table-tab">
        {{ $t("places.address.address") }}
      </v-tab>
      <v-tab-item>
        <PlacesTable
          v-bind:addresses="addressList"
          v-bind:areas="areaList"
          v-bind:locations="locationList"
          v-bind:countries="countryList"
          v-on:fetchPlacesList="fetchPlacesList"
        ></PlacesTable>
      </v-tab-item>
      <v-tab ripple data-cy="area-table-tab">
        {{ $t("places.area.area") }}
      </v-tab>
      <v-tab-item>
        <AreaTable
          v-bind:addresses="addressList"
          v-bind:areas="areaList"
          v-bind:locations="locationList"
          v-bind:countries="countryList"
          v-on:fetchPlacesList="fetchPlacesList"
        ></AreaTable>
      </v-tab-item>
    </v-tabs>
  </v-container>
</template>

<script>
import PlacesTable from "../components/places/PlacesTable";
import AreaTable from "../components/places/AreaTable";
import { isEmpty } from "lodash";

export default {
  name: "Places",
  components: { PlacesTable, AreaTable },
  data() {
    return {
      addressList: [],
      areaList: [],
      locationList: [],
      countryList: [],
    };
  },

  mounted() {
    this.fetchPlacesList();
  },

  methods: {
    fetchPlacesList(filters = {}) {
      console.log(filters);
      if (isEmpty(filters)) {
        console.log("no filters applied");
        this.$http.get("/api/v1/places/addresses").then((resp) => {
          this.addressList = resp.data;
        });
      } else {
        console.log("filters applied");
        // USE IFS TO CONCATENATE STRING TOGETHER DEPENDING ON FIELDS BEING EMPTY OR NOT TO AVOID NANS
        let requestString = `/api/v1/places/addresses?`;
        if (!isNaN(parseFloat(filters.startLatitude))) {
          requestString += `&lat_start=${parseFloat(filters.startLatitude)}`;
        }
        if (!isNaN(parseFloat(filters.endLatitude))) {
          requestString += `&lat_end=${parseFloat(filters.endLatitude)}`;
        }
        if (!isNaN(parseFloat(filters.startLongitude))) {
          requestString += `&lon_start=${parseFloat(filters.startLongitude)}`;
        }
        if (!isNaN(parseFloat(filters.endLongitude))) {
          requestString += `&lon_end=${parseFloat(filters.endLongitude)}`;
        }
        if (!isNaN(parseFloat(filters.specificLatitude))) {
          requestString += `&dist_lat=${parseFloat(filters.specificLatitude)}`;
        }
        if (!isNaN(parseFloat(filters.specificLongitude))) {
          requestString += `&dist_lng=${parseFloat(filters.specificLongitude)}`;
        }
        if (!isNaN(parseFloat(filters.distance))) {
          requestString += `&dist=${parseFloat(filters.distance)}`;
        }
        if (
          !isEmpty(filters.address) &&
          !isNaN(parseFloat(filters.address.latitude)) &&
          !isNaN(parseFloat(filters.address.longitude))
        ) {
          requestString += `&dist_addr_lat=${parseFloat(
            filters.address.latitude
          )}`;
          requestString += `&dist_addr_lng=${parseFloat(
            filters.address.longitude
          )}`;
          requestString += `&dist_addr=${parseFloat(filters.addressDistance)}`;
        }
        this.$http.get(requestString).then((resp) => {
          this.addressList = resp.data;
        });
      }
      this.$http.get("/api/v1/places/areas").then((resp) => {
        this.areaList = resp.data;
      });
      this.$http.get("/api/v1/places/locations").then((resp) => {
        this.locationList = resp.data;
        console.log(this.locationList);
      });
      this.$http.get("/api/v1/places/countries").then((resp) => {
        this.countryList = resp.data;
      });
    },
  },
};
</script>

<style scoped></style>
