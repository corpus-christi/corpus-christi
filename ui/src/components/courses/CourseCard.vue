<template>
  <v-container>
    <v-layout>
      <v-flex>
        <v-toolbar color="cyan" dark>
          <v-toolbar-title> {{ course.title }} </v-toolbar-title>
        </v-toolbar>
        <v-card>
          <v-card-text>{{ course.description }}</v-card-text>
          <v-card-text
            >{{ $t("courses.enrolled") }}: {{ course.enrolled }}</v-card-text
          >
          <v-card-actions> <slot name="actions"></slot> </v-card-actions>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
export default {
  name: "CourseCard",
  // data() {
  //   return {
  //     title: "New Testament",
  //     description: "extra test",
  //     enrolled: 0
  //   };
  // },
  props: ["course"]
};
</script>
