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
      @click="markerSelected(m)"
    >
      <GmapInfoWindow
        :position="m.position"
        :opened="m.opened"
        @closeclick="close(m)"
      >
        <div>
          <h2>{{ m.data.name }}</h2>
          <p>{{ m.data.description }}</p>
        </div>
      </GmapInfoWindow>
    </gmap-marker>
  </gmap-map>
</template>

<script>
export default {
  name: "GoogleMap",
  data() {
    return {
      center: { lat: -2.90548355117024, lng: -79.02949294174876 },
      zoom: 13
    };
  },
  methods: {
    markerSelected(m) {
      for (let marker of this.$props.markers) {
        marker.opened = false;
      }
      this.$refs.gmap.$mapPromise.then(map => {
        map.panTo(m.position);
      });
      m.opened = true;
    },
    close(m) {
      m.opened = false;
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
