<template>
  <v-card>
    <div class="body">
      <!-- Display course title, description and register button -->
        <v-card-title>
          <v-layout row align-center justify-center>
            <v-flex shrink>
              <span class="headline mb-3">{{ course.title }}</span>
            </v-flex>
          </v-layout>
        </v-card-title>

        <v-card-text class="text">
          <v-layout>
            <v-flex>
              <div class="mb-3">{{ course.description }}</div>
            </v-flex>
          </v-layout>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn raised color="primary">{{ $t("courses.course.register") }}</v-btn>
          <v-spacer></v-spacer>
        </v-card-actions>
      </div>
    <v-card>
</template>

<script>
export default {
  name: "CourseCard",
  props:{ 
    course: {}
  },
  data() {
    return {};
  }
  
};
</script>

<style scoped>
.text {
  max-height: 200px;
  min-height: 200px;
}

.card {
  margin: 25px;
  border-radius: 30px;
}

.body {
  padding-top: 10px;
  border-radius: 30px;
}
</style>