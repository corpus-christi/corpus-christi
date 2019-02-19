<template>
  <div>
    <v-btn
      outline
      color="primary"
      v-on:click="
        $router.push({ name: 'course-details', params: { courseId } })
      "
      ><v-icon>arrow_back</v-icon>{{ $t("actions.back") }}</v-btn
    >
    <v-tabs color="transparent" slider-color="accent">
      <v-tab :to="{ name: 'course-offering-details' }"
        ><v-icon>list</v-icon>&nbsp;{{ $t("events.details.title") }}</v-tab
      >
      <v-tab :to="{ name: 'course-offering-students', params: { offeringId } }"
        ><v-icon>person </v-icon>&nbsp;{{ $t("courses.students") }}</v-tab
      >
      <v-tab :to="{ name: 'course-offering-meetings' }"
        ><v-icon>calendar_today</v-icon>&nbsp;{{
          $t("courses.schedule")
        }}</v-tab
      >
    </v-tabs>
    <hr class="vertical-spacer" />
    <router-view />
  </div>
</template>

<script>
export default {
  name: "CourseOffering",
  props: {
    courseId: {
      type: [String, Number],
      required: true
    },
    offeringId: {
      type: [String, Number],
      required: true
    }
  }
};
</script>

<style>
.vertical-spacer {
  margin-bottom: 16px;
}
</style>
