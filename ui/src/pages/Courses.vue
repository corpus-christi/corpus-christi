<template>
  <v-container>
      <h1>Hello, Courses</h1>
      <CourseCard/>
  </v-container>
</template>

<script>
import CourseCard from "../components/courses/CourseCard";

export default {
  name: "Courses",
  components: {
      CourseCard
  }
};
</script>

<style scoped></style>
