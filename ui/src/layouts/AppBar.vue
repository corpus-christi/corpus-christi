<template>
  <!-- Creates the Bar -->
  <nav>
    <arco-app-bar v-if="$route.meta.layout === 'arco'" />
    <standard-app-bar v-else />
  </nav>
</template>

<script>
/**
 * @file
 * @name AppBar.vue
 */
import StandardAppBar from "./app-bars/StandardAppBar";
import ArcoAppBar from "./app-bars/ArcoAppBar";

/**
 * @module
 * @name AppBar
 * @exports ./DefaultLayout.vue
 * Operates the Bar across the top of the Screen for all pages.
 * Allows customization of the public-facing application bar for private label use of the software.
 */
export default {
  name: "AppBar",
  components: { StandardAppBar, ArcoAppBar },
};
</script>
