<template>
  <v-container> <DiplomasTable v-bind:course="course" /> </v-container>
</template>

<script>
import DiplomasTable from "../components/diplomas/DiplomasTable";
export default {
  name: "Diplomas",
  components: {
    DiplomasTable
  },
  props: ["course"]
};
</script>

<style scoped></style>
