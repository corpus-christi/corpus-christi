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

export default {
  name: "Places",
  components: { PlacesTable, AreaTable },
  data() {
    return {
      addressList: [],
      areaList: [],
      locationList: [],
      countryList: []
    };
  },

  mounted() {
    this.fetchPlacesList();
  },

  methods: {
    fetchPlacesList() {
      this.$http.get("/api/v1/places/addresses").then(resp => {
        this.addressList = resp.data;
      });
      this.$http.get("/api/v1/places/areas").then(resp => {
        this.areaList = resp.data;
      });
      this.$http.get("/api/v1/places/locations").then(resp => {
        this.locationList = resp.data;
        console.log(this.locationList);
      });
      this.$http.get("/api/v1/places/countries").then(resp => {
        this.countryList = resp.data;
      });
    }
  }
};
</script>

<style scoped></style>
