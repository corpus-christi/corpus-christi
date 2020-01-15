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
      @click="openInfoWindow(m)"
    />
    <gmap-info-window
      :options="{maxWidth: 300}"
      :position="infoWindow.position"
      :opened="infoWindow.open"
      @closeclick="infoWindow.open = false"
    >
      {{ infoWindow.name }} <br>
      {{ infoWindow.description }}
    </gmap-info-window>
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
      this.map.panTo(position);
      this.infoWindow.position = position;
      this.infoWindow.open = true;
    },
    openInfoWindow(item) {
      this.centerMapOnMarker(item.position);
      this.infoWindow.name = item.data.name;
      this.infoWindow.description = item.data.description;
    }
  },
  data() {
    return {
      center: { lat: -2.90548355117024, lng: -79.02949294174876 },
      zoom: 15,
      map: "",
      infoWindow: {
        position: {lat: 0, lng: 0},
        open: false,
        address: "",
        name: "",
        description: ""
      }
    };
  },
  mounted: function() {
    this.$refs.map.$mapPromise.then(m => {
      this.map = m;
    });
  }
};
</script>
