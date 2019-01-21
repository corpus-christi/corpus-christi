<template>
  <gmap-map
    ref="gmap"
    v-bind:center="center"
    v-bind:zoom="zoom"
    style="width:100%;  height: 400px;"
    data-cy="gmap"
  >
    <gmap-marker
      v-for="(m, index) in markers"
      :key="index"
      :position="m.position"
      @click="centerMapOnPosition"
    ></gmap-marker>
  </gmap-map>
</template>

<script>
export default {
  name: "GoogleMap",
  data() {
    return {
      center: { lat: -2.90548355117024, lng: -79.02949294174876 },
      zoom: 15
    };
  },
  methods: {
    centerMapOnPosition(position) {
      this.$refs.gmap.panTo(position.latLng);
    }
  },
  props: {
    markers: {
      type: Array,
      required: true
    }
  }
};
</script>
