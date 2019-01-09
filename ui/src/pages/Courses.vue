<template>
  <v-container>
<<<<<<< HEAD
    <CoursesTable v-bind:course="course"/>
=======
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
>>>>>>> feature/courses-33_creating-a-new-course-ui-slots
  </v-container>
</template>

<script>
<<<<<<< HEAD
import CoursesTable from "../components/courses/CoursesTable";
=======
import CourseCard from "../components/courses/CourseCard";
import CourseAdminActions from "../components/courses/CourseAdminActions";
>>>>>>> feature/courses-33_creating-a-new-course-ui-slots

export default {
  name: "Courses",
  components: {
<<<<<<< HEAD
    CoursesTable
  },
  props: [
    'course'
  ]
=======
    CourseCard,
    CourseAdminActions
  }
>>>>>>> feature/courses-33_creating-a-new-course-ui-slots
};
</script>

<style scoped></style>
