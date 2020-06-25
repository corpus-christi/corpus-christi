<template>
  <v-container> <router-view :key="$route.path"></router-view> </v-container>
</template>

<script>
export default {
  name: "Groups"
};
</script>
