<template>
  <v-card>
    <v-card-title>{{courseTitle}}</v-card-title>
    <v-card-text>{{description}}</v-card-text>
    <v-card-action>
      <v-btn flat>{{$t("actions.edit")}}</v-btn>
    </v-card-action>
  </v-card>
</template>

<script>
export default {
  name: "CourseCard",
  data() {
    return {
      courseTitle: "test",
      description: "extra test",
      enrolled: 0
    };
  }
};
</script>
