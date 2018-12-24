<template>
  <v-container>
    <PersonTable />
  </v-container>
</template>

<script>
import PersonTable from "../components/PersonTable";

export default {
  name: "People",
  components: { PersonTable }
};
</script>

<style scoped></style>
