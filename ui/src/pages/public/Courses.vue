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
        v-for="course in courses"
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

export default {
  name: "Courses",
  components: {
    CourseCard
  },
  data() {
    return {
      courses: [],
      pageLoaded: false,
      showDatePicker: false
    };
  },
  mounted() {
    this.pageLoaded = false;
    this.$http.get("/api/v1/courses/courses").then(resp => {
      this.courses = resp.data;
      console.log(resp.data);
      this.pageLoaded = true;
    });
  },
  
  computed: {
    today() {
      return this.getDateFromTimestamp(Date.now());
    },
    
    ...mapGetters(["currentLanguageCode"])
  },
  
  methods: {
    getDateFromTimestamp(ts) {
      let date = new Date(ts);
      if (date.getTime() < 86400000) {
        //ms in a day
        return "";
      }
      let yr = date.toLocaleDateString(this.currentLanguageCode, {
        year: "numeric"
      });
      let mo = date.toLocaleDateString(this.currentLanguageCode, {
        month: "2-digit"
      });
      let da = date.toLocaleDateString(this.currentLanguageCode, {
        day: "2-digit"
      });
      return `${yr}-${mo}-${da}`;
    },

    getTimestamp(date) {
      let datems = new Date(date).getTime();
      let tzoffset = new Date().getTimezoneOffset() * 60000;
      return new Date(datems + tzoffset);
    },

    addDaystoDate(date, dayDuration) {
      let date1 = this.getTimestamp(date);
      date1.setDate(date1.getDate() + dayDuration);
      return this.getDateFromTimestamp(date1);
    }
  }
};
</script>

<style scoped></style>
