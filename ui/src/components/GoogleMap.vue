<template>
  <GmapMap
    ref="mapRef"
    v-bind:center="center"
    v-bind:zoom="zoom"
    style="width:100%;  height: 400px;"
    data-cy="gmap"
  >
    <GmapMarker
      :key="index"
      v-for="(m, index) in markers"
      :position="m.position"
      @click="openInfoWindow(m)"
    />
    <GmapInfoWindow
      :options="{ maxWidth: 300 }"
      :position="infoWindow.position"
      :opened="infoWindow.open"
      @closeclick="infoWindow.open = false"
    >
      {{ infoWindow.name }} <br />
      {{ infoWindow.address }} <br />
      {{ infoWindow.description }}
    </GmapInfoWindow>
  </GmapMap>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";

defineProps<{
  markers?: Array<{
    position: { lat: number; lng: number };
    data: { name: string; address: string; description?: string };
  }>;
}>();

const center = ref({ lat: -2.90548355117024, lng: -79.02949294174876 });
const zoom = ref(15);
const map = ref<any>(null);
const mapRef = ref<any>(null);
const infoWindow = ref({
  position: { lat: 0, lng: 0 },
  open: false,
  address: "",
  name: "",
  description: ""
});

function centerMapOnMarker(position: { lat: number; lng: number }) {
  map.value?.panTo(position);
  infoWindow.value.position = position;
  infoWindow.value.open = true;
}

function openInfoWindow(item: any) {
  centerMapOnMarker(item.position);
  infoWindow.value.name = item.data.name;
  infoWindow.value.description = item.data.description;
  infoWindow.value.address = item.data.address;
}

onMounted(() => {
  if (mapRef.value) {
    mapRef.value.$mapPromise.then((m: any) => {
      map.value = m;
    });
  }
});
</script>
