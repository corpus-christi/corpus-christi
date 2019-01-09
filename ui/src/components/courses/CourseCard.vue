<template>
    <v-container>
      <v-layout>
        <v-flex>
          <v-toolbar color="cyan" dark>
            <v-toolbar-title>
              {{course.title}}
            </v-toolbar-title>
          </v-toolbar>
          <v-card>
            <v-card-text>{{course.description}}</v-card-text>
            <v-card-text>{{$t("courses.enrolled")}}: {{course.enrolled}}</v-card-text>
<<<<<<< HEAD
              <v-card-actions>
                <v-layout align-center justify-end>
                  <v-btn flat @click="showForm">{{$t("actions.edit")}}</v-btn>
                </v-layout>
              </v-card-actions>
=======
            <v-card-actions>
              <slot name="actions"></slot>
            </v-card-actions>
>>>>>>> feature/courses-33_creating-a-new-course-ui-slots
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
  props: [
    'course'
  ],
  methods: {
    showForm() {
      
    }
  }
};
</script>
