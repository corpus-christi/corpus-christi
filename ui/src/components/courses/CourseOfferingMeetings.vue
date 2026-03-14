<template>
  <div>
    <v-toolbar>
      <v-toolbar-title>{{ t("courses.schedule") }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="search"
        v-bind:label="t('actions.search')"
        single-line
        hide-details
      ></v-text-field>
      <v-spacer></v-spacer>
      <v-btn color="primary" @click.stop="newClassMeeting">
        <v-icon dark start>event</v-icon>
        {{ t("courses.add-meeting") }}
      </v-btn>
    </v-toolbar>
    <v-data-table
      :headers="headers"
      :items="meetings"
      :search="search"
      :loading="loading"
      class="elevation-1"
    >
      <template #item="{ item }">
        <tr>
          <td>{{ item.displayDate }}</td>
          <td>{{ item.location?.description }}</td>
          <td>{{ item.teacher?.compositeName }}</td>
          <td>
            <v-row align="center" justify="end" no-gutters>
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <v-btn
                    variant="outlined"
                    icon
                    size="small"
                    color="primary"
                    v-bind="props"
                    @click="editClassMeeting(item)"
                  >
                    <v-icon size="small">edit</v-icon>
                  </v-btn>
                </template>
                <span>{{ t("actions.edit") }}</span>
              </v-tooltip>
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <v-btn
                    variant="outlined"
                    icon
                    size="small"
                    color="primary"
                    v-bind="props"
                    @click="openAttendance(item)"
                  >
                    <v-icon size="small">assignment_ind</v-icon>
                  </v-btn>
                </template>
                <span>{{ t("courses.class-attendance") }}</span>
              </v-tooltip>
            </v-row>
          </td>
        </tr>
      </template>
    </v-data-table>

    <!-- New/Edit dialog -->
    <v-dialog
      persistent
      scrollable
      v-model="classMeetingDialog.show"
      max-width="500px"
    >
      <ClassMeetingForm
        v-bind:editMode="classMeetingDialog.editMode"
        v-bind:initialData="classMeetingDialog.classMeeting"
        v-bind:offeringId="offeringId"
        v-on:cancel="cancelClassMeeting"
        v-on:save="saveClassMeeting"
      />
    </v-dialog>

    <!-- Attendance dialog -->
    <v-dialog
      persistent
      scrollable
      v-model="attendanceDialog.show"
      max-width="500px"
    >
      <ClassAttendance
        :classMeeting="attendanceDialog.classMeeting"
        @cancel="cancelAttendance"
        @save="saveAttendance"
      />
    </v-dialog>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false">{{
          t("actions.close")
        }}</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import { useAuthStore } from "@/stores/auth";
import ClassMeetingForm from "./ClassMeetingForm.vue";
import ClassAttendance from "./ClassAttendance.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const route = useRoute();
const authStore = useAuthStore();

const props = defineProps<{
  offeringId: string | number;
}>();

const loading = ref(true);
const loadingFailed = ref(false);
const meetings = ref<any[]>([]);
const search = ref("");

const classMeetingDialog = ref({
  show: false,
  editMode: false,
  classMeeting: {} as Record<string, any>
});

const attendanceDialog = ref({
  show: false,
  classMeeting: {} as Record<string, any>
});

const snackbar = ref({ show: false, text: "" });

const headers = computed(() => [
  { title: t("courses.when"), value: "displayDate", width: "33%" },
  { title: t("courses.location"), value: "location.description", width: "33%" },
  { title: t("courses.teacher"), value: "teacher.compositeName", width: "33%" },
  { title: t("actions.header"), sortable: false }
]);

watch(route, () => {
  loadMeetings();
});

watch(() => authStore.currentLanguageCode, () => {
  updateCompositeProperties();
});

function loadMeetings() {
  loading.value = true;
  loadingFailed.value = false;
  http
    .get(`/api/v1/courses/course_offerings/${props.offeringId}/class_meetings`)
    .then(resp => {
      meetings.value = resp.data;
      updateCompositeProperties();
    })
    .catch(err => {
      console.log("LOAD MEETINGS ERR", err);
      loadingFailed.value = true;
    })
    .finally(() => {
      loading.value = false;
    });
}

function updateCompositeProperties() {
  meetings.value.forEach(meeting => {
    meeting.teacher.compositeName =
      meeting.teacher.firstName + " " + meeting.teacher.lastName;
    meeting.displayDate = getDisplayDate(meeting.when);
    return meeting;
  });
}

function activateClassMeetingDialog(classMeeting: Record<string, any> = {}, editMode = false) {
  classMeetingDialog.value.editMode = editMode;
  classMeetingDialog.value.classMeeting = classMeeting;
  classMeetingDialog.value.show = true;
}

function editClassMeeting(classMeeting: any) {
  activateClassMeetingDialog({ ...classMeeting }, true);
}

function newClassMeeting() {
  activateClassMeetingDialog();
}

function cancelClassMeeting() {
  classMeetingDialog.value.show = false;
}

function saveClassMeeting(newMeetings: any) {
  if (newMeetings instanceof Error) {
    snackbar.value.text = classMeetingDialog.value.editMode
      ? t("courses.update-meeting-failed")
      : t("courses.add-meeting-failed");
    snackbar.value.show = true;
    classMeetingDialog.value.show = false;
    return;
  }

  if (classMeetingDialog.value.editMode) {
    let meeting = newMeetings[0];
    const idx = meetings.value.findIndex(c => c.id === meeting.id);
    Object.assign(meetings.value[idx], meeting);
    snackbar.value.text = t("courses.meeting-updated");
  } else {
    for (let meeting of newMeetings) {
      meeting.displayDate = getDisplayDate(meeting.when);
      meeting.teacher.compositeName =
        meeting.teacher.firstName + " " + meeting.teacher.lastName;
    }
    meetings.value.push(...newMeetings);
    snackbar.value.text = t("courses.meeting-added");
  }

  snackbar.value.show = true;
  classMeetingDialog.value.show = false;
}

function openAttendance(meeting: any) {
  attendanceDialog.value.classMeeting = meeting;
  attendanceDialog.value.show = true;
}

function cancelAttendance() {
  attendanceDialog.value.show = false;
}

function saveAttendance(attendance: any) {
  if (attendance instanceof Error) {
    snackbar.value.text = t("courses.class-attendance-update-failed");
  } else {
    snackbar.value.text = t("courses.class-attendance-updated");
  }

  snackbar.value.show = true;
  attendanceDialog.value.show = false;
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

onMounted(() => {
  loadMeetings();
});
</script>

<style></style>
