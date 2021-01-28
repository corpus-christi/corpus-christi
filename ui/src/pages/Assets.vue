locale
<template>
  <v-container> <AssetTable /> </v-container>
</template>

<script>
/**
 * @file
 * @name Assets.vue
 */
import AssetTable from "../components/assets/AssetTable";

/**
 * @module
 * @name Assets
 * @exports ../router.js
 * Draws the /assets page
 */
export default {
  name: "Assets",
  components: { AssetTable },
};
</script>

<style scoped></style>
