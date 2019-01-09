<template>
  <gmap-map
    v-bind:center="center"
    v-bind:zoom="zoom"
    style="width:100%;  height: 400px;"
    data-cy=""
  ></gmap-map>
</template>

<script>
export default {
  name: "GoogleMap",
  data() {
    return {
      center: { lat: -2.90548355117024, lng: -79.02949294174876 },
      zoom: 15
    };
  }
};
</script>
