<template>
  <v-container>
      <h1>Hello, Courses</h1>
      <v-container grid-list-md>
        <v-layout row wrap>
          <v-flex md3 v-for="course in courses" :key="course">
            <CourseCard v-bind:course="course">
              <template slot="actions">
                <CourseAdminActions v-bind:course="course"/>
              </template>
            </CourseCard>
          </v-flex>
        </v-layout>
      </v-container>
  </v-container>
</template>

<script>
import CourseCard from "../components/courses/CourseCard";
import CourseAdminActions from "../components/courses/CourseAdminActions";

export default {
  name: "Courses",
  data() {
    return {
      courses: [
        {title: "New Testament", description: "study of the new Testament", enrolled: 10}, 
        {title: "Old Testament", description: "study of the old Testament", enrolled: 2}
      ]
    };
  },
  components: {
    CourseCard,
    CourseAdminActions
  }
};
</script>

<style scoped></style>
