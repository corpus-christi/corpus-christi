<template>
  <v-card>
    <v-card-title>
      <span class="headline">
        {{ t("courses.class-attendance-for") }}
        {{ getDisplayDate(classMeeting.when) }}
      </span>
    </v-card-title>
    <v-card-text>
      <template v-if="loading">
        <v-progress-linear indeterminate color="primary" />
      </template>
      <template v-else-if="loadingFailed">
        {{ t("courses.class-attendance-load-failed") }}
      </template>
      <template v-else>
        <v-list>
          <v-list-item v-for="student of students" :key="student.id">
            <template #prepend>
              <v-checkbox v-model="student.present" />
            </template>
            <v-list-item-title>
              {{ student.person.firstName }} {{ student.person.lastName }}
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </template>
    </v-card-text>
    <v-card-actions>
      <v-btn color="secondary" variant="text" :disabled="saving" v-on:click="cancel">{{
        t("actions.cancel")
      }}</v-btn>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        :disabled="saving"
        :loading="saving"
        v-on:click="save"
      >
        {{ t("actions.save") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import { useAuthStore } from "@/stores/auth";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const authStore = useAuthStore();

const props = defineProps<{
  classMeeting: Record<string, any>;
}>();

const emit = defineEmits(["cancel", "save"]);

const loading = ref(false);
const loadingFailed = ref(false);
const saving = ref(false);
const students = ref<any[]>([]);

watch(() => props.classMeeting, () => {
  load();
});

function load() {
  loading.value = true;
  loadingFailed.value = false;

  let promises: Promise<any>[] = [];
  promises.push(
    http
      .get(
        `/api/v1/courses/course_offerings/${props.classMeeting.offeringId}/${props.classMeeting.id}/class_attendance`
      )
      .then(resp => resp.data.attendance)
  );

  promises.push(
    http
      .get(
        `/api/v1/courses/course_offerings/${props.classMeeting.offeringId}/students`
      )
      .then(resp => {
        students.value = resp.data.filter(
          (student: any) => student.active && student.confirmed
        );
      })
  );

  Promise.all(promises)
    .then(values => {
      let attendance = values[0];
      applyAttendance(attendance);
    })
    .catch(err => {
      console.log("LOAD ERR", err);
      loadingFailed.value = true;
    })
    .finally(() => {
      loading.value = false;
    });
}

function applyAttendance(attendance: any[]) {
  students.value.forEach(student => {
    student.present = !!attendance.find(
      record => record.studentId == student.id
    );
  });
}

function cancel() {
  emit("cancel");
}

function save() {
  saving.value = true;
  let attendance = students.value
    .filter(student => student.present)
    .map(student => student.id);

  http
    .patch(
      `/api/v1/courses/course_offerings/${props.classMeeting.offeringId}/${props.classMeeting.id}/class_attendance`,
      { attendance }
    )
    .then(resp => {
      console.log("ATTENDANCE", resp);
      emit("save", resp.data);
    })
    .catch(err => {
      console.log("ATTENDANCE ERR", err);
      emit("save", err);
    })
    .finally(() => {
      saving.value = false;
    });
}

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
</script>

<style></style>
