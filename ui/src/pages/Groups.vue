<template>
  <v-container>
    <router-view :key="$route.path" />
  </v-container>
</template>

<script>
export default {
  name: "Groups",
};
</script>
