<template>
  <v-container>
    <PersonTable />
    <v-flex d-flex xs12 sm6 md4> <PersonForm /> </v-flex>
  </v-container>
</template>

<script>
import PersonForm from "@/components/PersonForm";
import PersonTable from "../components/PersonTable";

export default {
  name: "People",
  components: { PersonTable, PersonForm }
};
</script>

<style scoped></style>
