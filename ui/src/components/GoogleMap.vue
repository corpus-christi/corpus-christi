<template>
  <gmap-map
    ref="map"
    v-bind:center="center"
    v-bind:zoom="zoom"
    style="width:100%;  height: 400px;"
    data-cy="gmap"
    ><gmap-marker
      :key="index"
      v-for="(m, index) in markers"
      :position="m.position"
      @click="centerMapOnMarker"
    ></gmap-marker>
  </gmap-map>
</template>

<script>
export default {
  name: "GoogleMap",
  props: {
    markers: {
      type: Array,
      required: false
    }
  },
  methods: {
    centerMapOnMarker(position) {
      this.map.panTo(position.latLng);
    }
  },
  data() {
    return {
      center: { lat: -2.90548355117024, lng: -79.02949294174876 },
      zoom: 15,
      map: ""
    };
  },
  mounted: function() {
    this.$refs.map.$mapPromise.then(m => {
      this.map = m;
    });
  }
};
</script>
