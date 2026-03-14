<template>
  <nav>
    <ArcoToolbar v-if="route.meta.layout === 'arco'" />
    <StandardToolbar v-else />
  </nav>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import ArcoToolbar from "./toolbars/Arco.vue";
import StandardToolbar from "./toolbars/Standard.vue";

const route = useRoute();
</script>
