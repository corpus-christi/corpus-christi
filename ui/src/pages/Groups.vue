<template>
  <v-container>
    <router-view :key="$route.path" />
  </v-container>
</template>

<script>
/**
 * @file
 * @name Groups.vue
 */

/**
 * @module
 * @name Groups
 * @exports ../router.js
 * Draws the base webpage for /groups. Because 'groups' always has children, most of the webpages are stored in ui/src/components/groups.
 */
export default {
  name: "Groups",
};
</script>
