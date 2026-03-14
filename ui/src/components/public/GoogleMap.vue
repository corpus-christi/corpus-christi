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

<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{
  markers: any[];
}>();

const gmap = ref<any>(null);
const center = ref({ lat: -2.90548355117024, lng: -79.02949294174876 });
const zoom = ref(13);

function markerSelected(m: any) {
  for (let marker of props.markers) {
    marker.opened = true;
  }
  if (gmap.value && gmap.value.$mapPromise) {
    gmap.value.$mapPromise.then((map: any) => {
      map.panTo(m.position);
    });
  }
  m.opened = true;
}

function close(m: any) {
  m.opened = false;
}
</script>
