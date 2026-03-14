<template>
  <div>
    <v-btn
      variant="outlined"
      color="primary"
      v-on:click="
        router.push({ name: 'course-details', params: { courseId } })
      "
      ><v-icon>arrow_back</v-icon>{{ t("actions.back") }}</v-btn
    >
    <v-tabs color="transparent" slider-color="accent">
      <v-tab :to="{ name: 'course-offering-details' }"
        ><v-icon>list</v-icon>&nbsp;{{ t("events.details.title") }}</v-tab
      >
      <v-tab :to="{ name: 'course-offering-students', params: { offeringId } }"
        ><v-icon>person </v-icon>&nbsp;{{ t("courses.students") }}</v-tab
      >
      <v-tab :to="{ name: 'course-offering-meetings' }"
        ><v-icon>calendar_today</v-icon>&nbsp;{{
          t("courses.schedule")
        }}</v-tab
      >
    </v-tabs>
    <hr class="vertical-spacer" />
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";

const { t } = useI18n();
const router = useRouter();

const props = defineProps<{
  courseId: string | number;
  offeringId: string | number;
}>();
</script>

<style>
.vertical-spacer {
  margin-bottom: 16px;
}
</style>
