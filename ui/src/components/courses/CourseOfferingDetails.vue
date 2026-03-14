<template>
  <v-row>
    <v-col cols="12" sm="12">
      <v-card>
        <template v-if="pageLoaded">
          <v-container fill-height fluid>
            <v-col>
              <v-col cols="9" sm="9" class="align-end">
                <span class="headline">{{ courseOffering.course?.name }}</span>
              </v-col>
              <v-card-text class="pa-4">
                <b>{{ t("courses.description") }}:</b>
                <div class="ml-2">{{ courseOffering.description }}</div>
                <b>{{ t("courses.enrolled") }}:</b>
                <div class="ml-2">
                  {{ studentsAmt + " / " + courseOffering.maxSize }}
                </div>
              </v-card-text>
            </v-col>
          </v-container>
        </template>
        <v-row v-else justify="center" style="height: 500px;">
          <div class="ma-5 pa-5">
            <v-progress-circular
              indeterminate
              color="primary"
            ></v-progress-circular>
          </div>
        </v-row>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import { useAuthStore } from "@/stores/auth";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const authStore = useAuthStore();

const props = defineProps<{
  offeringId?: any;
}>();

const courseOffering = ref<Record<string, any>>({});
const studentsAmt = ref(0);
const snackbar = ref({ show: false, text: "" });
const pageLoaded = ref(false);

function getDisplayDate(ts: any) {
  let date = new Date(ts);
  return date.toLocaleTimeString(authStore.currentLanguageCode, {
    year: "numeric",
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });
}

onMounted(() => {
  pageLoaded.value = false;
  const id = props.offeringId;

  http
    .get(`/api/v1/courses/course_offerings/${id}/students`)
    .then(resp => {
      studentsAmt.value = resp.data.filter((student: any) => student.active).length;
    });

  http.get(`/api/v1/courses/course_offerings/${id}`).then(resp => {
    courseOffering.value = resp.data;
    pageLoaded.value = true;
  });
});
</script>

<style scoped>
.multi-line {
  white-space: pre;
}
</style>
