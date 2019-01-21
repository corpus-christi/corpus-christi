<template>
  <v-container>
    <CourseOfferingsTable v-bind:course="courseOffering" />
  </v-container>
</template>

<script>
import CourseOfferingsTable from "../components/courses/CourseOfferingsTable";

export default {
  name: "course-offerings-admin",
  components: {
    CourseOfferingsTable
  },
  props: ["courseOffering"]
};
</script>

<style scoped></style>
