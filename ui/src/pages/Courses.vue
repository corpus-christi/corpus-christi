<template>
  <v-container> <CoursesTable v-bind:course="course" /> </v-container>
</template>

<script>
import CoursesTable from "../components/courses/CoursesTable";

export default {
  name: "Courses",
  components: {
    CoursesTable
  },
  props: ["course"]
};
</script>

<style scoped></style>
