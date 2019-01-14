<template>
  <form>
    <v-combobox
      v-model="prereqs"
      :items="items"
      v-bind:label="$t('courses.title')"
      chips
      clearable
      solo
      multiple
    ></v-combobox>

    <!-- description -->
    <v-text-field
      v-model="course.description"
      v-bind:label="$t('courses.description')"
      name="description"
    ></v-text-field>

    <!-- teacher -->
    <v-text-field v-model="course.name" v-bind:label="teacher" name="location"></v-text-field>

    <!-- location -->
    <v-text-field v-model="course.name" v-bind:label="location" name="location"></v-text-field>

    <!-- date and time -->
    <v-layout row>
      <v-flex xs12 v-for="day in days" :key="day">
        <v-checkbox :label="day" :value="day" v-model="selectedDays"></v-checkbox>
      </v-flex>
    </v-layout>

    <!-- max size -->
    <v-text-field
      v-model="course.description"
      v-bind:label="$t('courses.description')"
      name="description"
    ></v-text-field>
  </form>
</template>

<script>
export default {
  name: "CourseOfferingForm",
  data: function() {
    return {
      availableCourses: [],
      prereqs: [],
      location: "location",
      teacher: "teacher",
      description: "description",
      days: ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"],
      selectedDays: []
    };
  },
  computed: {
    items() {
      return this.availableCourses.filter(item => item.id != this.course.id);
    }
  },
  props: {
    course: Object
  },
  methods: {
    remove(item) {
      this.prereqs.splice(this.prereqs.indexOf(item), 1);
      this.prereqs = [...this.prereqs];
    }
  },
  mounted() {
    this.$http
      .get("/api/v1/courses/courses")
      .then(
        resp => (this.availableCourses = resp.data.filter(item => item.active))
      );
  }
};
</script>
