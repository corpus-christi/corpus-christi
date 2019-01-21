<template>
  <v-container>
    <DiplomasTable />
  </v-container>
</template>

<script>
import DiplomasTable from "../components/diplomas/DiplomasTable";
export default {
  name: "Diplomas",
  components: {
    DiplomasTable
  },
  props: [
  ]
};
</script>

<style scoped></style>