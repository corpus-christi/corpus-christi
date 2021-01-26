<template>
  <!-- Creates the Footer -->
  <v-footer app dark color="grey" class="pa-2">
    <v-spacer />
    <div>
      &copy; Copyright 2018&ndash;{{ new Date().getFullYear() }}
      Taylor Center for Missions Computing
    </div>
  </v-footer>
</template>

<script>
/**
 * @file
 * @name Footer.vue
 */

/**
 * @module
 * @name Footer
 * @exports DefaultLayout.vue
 * Configures the Footer at the bottom of every page.
 */
export default {
  name: "Footer",
};
</script>
