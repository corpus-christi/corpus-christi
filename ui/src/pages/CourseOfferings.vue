<template>
  <v-container>
    <CourseOfferingsTable v-bind:course="courseOffering" />
  </v-container>
</template>

<script>
/**
 * @file
 * @name CourseOfferings.vue
 */
import CourseOfferingsTable from "../components/courses/CourseOfferingsTable";

/**
 * @module
 * @name CourseOfferings
 * @exports ???
 * Unused File.
 */
export default {
  name: "CourseOfferings",
  components: {
    CourseOfferingsTable,
  },
  props: ["courseOffering"],
};
</script>

<style scoped></style>
