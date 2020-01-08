<template>
  <v-container>
    <PlacesTable
      v-bind:addresses="addressList"
      v-bind:areas="areaList"
      v-bind:locations="locationList"
    ></PlacesTable>
  </v-container>
</template>

<script>
import PlacesTable from "../components/places/PlacesTable";

export default {
  name: "Places",
  components: { PlacesTable },
  data() {
    return {
      addressList: [],
      areaList: [],
      locationList: []
    };
  },

  mounted() {
    this.$http.get("/api/v1/places/addresses").then(resp => {
      this.addressList = resp.data;
    });
    this.$http.get("/api/v1/places/areas").then(resp => {
      this.areaList = resp.data;
    });
    this.$http.get("/api/v1/places/locations").then(resp => {
      this.locationList = resp.data;
    });
  }
};
</script>

<style scoped></style>
