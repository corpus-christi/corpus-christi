<template>
  <v-container> <CoursesTable v-bind:course="course" /> </v-container>
</template>

<script>
import CoursesTable from "../components/courses/CoursesTable";

export default {
  name: "course-offerings-admin",
  components: {
    CoursesTable
  },
  props: ["course"]
};
</script>

<style scoped></style>
