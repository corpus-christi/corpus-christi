<template>
  <v-container> <team-table /> </v-container>
</template>

<script>
import TeamTable from "../components/teams/TeamTable";

export default {
  name: "Teams",
  components: { "team-table":TeamTable }
};
</script>

<style scoped></style>