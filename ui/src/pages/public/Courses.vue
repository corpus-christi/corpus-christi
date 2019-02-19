<template>
  <v-container grid-list-md>
    <v-layout row wrap>
      <v-flex xs12 sm12 md4>
        <h1 style="margin-left: 25px;">
          {{ $t("public.headers.upcoming-classes") }}
        </h1>
      </v-flex>
    </v-layout>

    <!-- Cards -->
    <v-layout layout row wrap>
      <v-flex
        xs12
        sm6
        md4
        lg4
        v-for="course in offeredCourses"
        v-bind:key="course.id"
      >
        <CourseCard :course="course"></CourseCard>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import CourseCard from "../../components/public/CourseCard";
import { mapGetters } from "vuex";
import { isEmpty } from "lodash";

export default {
  name: "Courses",
  components: {
    CourseCard
  },
  data() {
    return {
      courses: [],
      course: {},
      pageLoaded: false
    };
  },
  mounted() {
    this.pageLoaded = false;
    this.$http.get("/api/v1/courses/courses").then(resp => {
      this.courses = resp.data.filter(course => course.active);
      this.pageLoaded = true;
    });
  },

  computed: {
    offeredCourses: function() {
      return this.courses.filter(course => {
        return !isEmpty(course.course_offerings);
      });
    },

    ...mapGetters(["currentLanguageCode"])
  },

  methods: {}
};
</script>
