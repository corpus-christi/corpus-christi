<template>
    <v-container> <PlacesTable /> </v-container>
</template>

<script>
import PlacesTable from "../components/places/PlacesTable";

export default {
  name: "Places",
  components: { PlacesTable }
};
</script>

<style scoped></style>
