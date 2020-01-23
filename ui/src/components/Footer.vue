<template>
  <v-footer app dark color="grey" class="pa-2">
    <v-spacer />
    <div>
      &copy; Copyright {{ new Date().getFullYear() }} Taylor Center for Missions
      Computing
    </div>
  </v-footer>
</template>

<script>
export default {
  name: "Footer"
};
</script>
