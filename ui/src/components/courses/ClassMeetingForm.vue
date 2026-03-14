<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <!-- date -->
        <v-row>
          <v-col cols="12" md="7">
            <v-menu
              v-model="showDatePicker"
              :close-on-content-click="false"
              :nudge-right="40"
              transition="scale-transition"
              offset-y
              min-width="290px"
            >
              <template #activator="{ props: menuProps }">
                <v-combobox
                  v-bind="menuProps"
                  v-model="dates"
                  :multiple="!editMode"
                  chips
                  small-chips
                  v-bind:label="t(editMode ? 'courses.date' : 'courses.dates')"
                  prepend-icon="event"
                  readonly
                  data-cy="course-offering-date"
                ></v-combobox>
              </template>
              <v-date-picker
                v-model="dates"
                :multiple="!editMode"
                no-title
                scrollable
                v-bind:locale="authStore.currentLanguageCode"
                data-cy="course-offering-date-picker"
              >
                <v-spacer></v-spacer>
                <v-btn
                  variant="text"
                  color="primary"
                  @click="showDatePicker = false"
                  data-cy="course-offering-date-cancel"
                  >{{ t("actions.cancel") }}</v-btn
                >
                <v-btn
                  variant="text"
                  color="primary"
                  @click="saveDateMenu"
                  data-cy="course-offering-date-ok"
                  >{{ t("actions.confirm") }}</v-btn
                >
              </v-date-picker>
            </v-menu>
          </v-col>

          <!-- time -->
          <v-col cols="12" md="4" class="ml-4">
            <v-menu
              v-model="showTimePicker"
              :close-on-content-click="false"
              :nudge-right="40"
              transition="scale-transition"
              offset-y
              min-width="290px"
            >
              <template #activator="{ props: menuProps }">
                <v-text-field
                  v-bind="menuProps"
                  v-model="time"
                  v-bind:label="t('courses.choose-time')"
                  prepend-icon="schedule"
                  readonly
                  data-cy="course-offering-time"
                ></v-text-field>
              </template>
              <v-time-picker
                v-if="showTimePicker"
                :format="timeFormat"
                v-model="time"
                data-cy="course-offering-time-picker"
              >
                <v-spacer></v-spacer>
                <v-btn
                  variant="text"
                  color="primary"
                  @click="showTimePicker = false"
                  data-cy="course-offering-time-cancel"
                  >{{ t("actions.cancel") }}</v-btn
                >
                <v-btn
                  variant="text"
                  color="primary"
                  @click="saveTimeMenu"
                  data-cy="course-offering-time-ok"
                  >{{ t("actions.confirm") }}</v-btn
                >
              </v-time-picker>
            </v-menu>
          </v-col>
        </v-row>

        <p class="caption" v-if="!editMode">
          {{ t("courses.info-meeting-dates") }}
        </p>

        <!-- teacher -->
        <EntitySearch
          person
          v-model="teacher"
          name="teacher"
          v-bind:error-messages="teacherErrors"
          :label="t('courses.teacher')"
          data-cy="course-offering-teacher"
        />

        <!-- location -->
        <EntitySearch
          location
          v-model="location"
          name="location"
          v-bind:error-messages="locationErrors"
          :label="t('courses.location')"
          data-cy="course-offering-location"
        />
      </form>
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
        <v-progress-circular
          v-if="!editMode"
          :size="20"
          :width="3"
          v-model="savingProgress"
        />
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import { isEmpty, clone, cloneDeep } from "lodash";
import EntitySearch from "../EntitySearch.vue";
import { useAuthStore } from "@/stores/auth";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const authStore = useAuthStore();

const props = defineProps<{
  editMode: boolean;
  initialData: Record<string, any>;
  offeringId: string | number;
}>();

const emit = defineEmits(["cancel", "save"]);

const saving = ref(false);
const savingProgress = ref(0);
const classMeeting = ref<Record<string, any>>({});
const dates = ref<any>("");
const time = ref("");
const teacher = ref<Record<string, any>>({});
const location = ref<Record<string, any>>({});
const showDatePicker = ref(false);
const showTimePicker = ref(false);
const teacherErrors = ref<string[]>([]);
const locationErrors = ref<string[]>([]);

const title = computed(() =>
  props.editMode ? t("actions.edit") : t("courses.new-meeting")
);

const timeFormat = computed(() => {
  if (authStore.currentLanguageCode === "en") return "ampm";
  else return "24hr";
});

watch(() => props.initialData, (prop) => {
  if (isEmpty(prop)) {
    clear();
  } else {
    classMeeting.value = prop;
    if (props.editMode) {
      dates.value = getDateFromTimestamp(classMeeting.value.when);
      time.value = getTimeFromTimestamp(classMeeting.value.when);
      teacher.value = classMeeting.value.teacher;
      location.value = classMeeting.value.location;
    }
  }
});

function saveDateMenu() {
  showDatePicker.value = false;
}

function saveTimeMenu() {
  showTimePicker.value = false;
}

function cancel() {
  clear();
  emit("cancel");
}

function clear() {
  dates.value = props.editMode ? "" : [];
  time.value = "";
  teacher.value = {};
  location.value = {};
  teacherErrors.value = [];
  locationErrors.value = [];
}

function validateForm(): boolean {
  teacherErrors.value = [];
  locationErrors.value = [];
  let valid = true;
  if (!teacher.value || !teacher.value.id) {
    teacherErrors.value = [t("validations.required")];
    valid = false;
  }
  if (!location.value || !location.value.id) {
    locationErrors.value = [t("validations.required")];
    valid = false;
  }
  return valid;
}

function save() {
  if (validateForm()) {
    saving.value = true;
    let meeting = cloneDeep(classMeeting.value);
    saveClassMeeting();
  }
}

function saveClassMeeting() {
  if (props.editMode) {
    let meeting: Record<string, any> = {};
    meeting.offeringId = props.offeringId;
    meeting.locationId = location.value.id;
    meeting.teacherId = teacher.value.id;
    meeting.when = getTimestamp(dates.value, time.value);

    http
      .patch(
        `/api/v1/courses/course_offerings/${props.offeringId}/${classMeeting.value.id}`,
        meeting
      )
      .then(resp => {
        let newMeeting = resp.data;
        newMeeting.location = location.value;
        newMeeting.teacher = teacher.value;
        emit("save", [newMeeting]);
      })
      .catch(err => {
        emit("save", err);
      })
      .finally(() => {
        saving.value = false;
      });
  } else {
    let meetingTemplate: Record<string, any> = {};
    meetingTemplate.offeringId = props.offeringId;
    meetingTemplate.locationId = location.value.id;
    meetingTemplate.teacherId = teacher.value.id;

    let meetings: Record<string, any>[] = [];
    const datesArr = Array.isArray(dates.value) ? dates.value : [dates.value];

    datesArr.forEach((date: string) => {
      let meeting = clone(meetingTemplate);
      meeting.when = getTimestamp(date, time.value);
      meetings.push(meeting);
    });

    let savingCount = 0;
    savingProgress.value = 0;

    let promises = meetings.map(meeting => {
      return http
        .post(
          `/api/v1/courses/course_offerings/${props.offeringId}/class_meetings`,
          meeting
        )
        .then(resp => {
          savingCount += 1;
          savingProgress.value = (100 * savingCount) / promises.length;

          let newMeeting = resp.data;
          newMeeting.location = location.value;
          newMeeting.teacher = teacher.value;
          return newMeeting;
        });
    });

    Promise.all(promises)
      .then(newMeetings => {
        emit("save", newMeetings);
      })
      .catch(err => {
        emit("save", err);
      })
      .finally(() => {
        saving.value = false;
      });
  }
}

function getTimestamp(date: string, time: string) {
  let datems = new Date(date).getTime();
  let timearr = time.split(":");
  let timemin = Number(timearr[0]) * 60 + Number(timearr[1]);
  let timems = timemin * 60000;
  let tzoffset = new Date().getTimezoneOffset() * 60000;
  return new Date(datems + timems + tzoffset);
}

function getDateFromTimestamp(ts: any) {
  let date = new Date(ts);
  if (date.getTime() < 86400000) {
    return "";
  }
  let yr = date.toLocaleDateString(authStore.currentLanguageCode, {
    year: "numeric"
  });
  let mo = date.toLocaleDateString(authStore.currentLanguageCode, {
    month: "2-digit"
  });
  let da = date.toLocaleDateString(authStore.currentLanguageCode, {
    day: "2-digit"
  });
  return `${yr}-${mo}-${da}`;
}

function getTimeFromTimestamp(ts: any) {
  let date = new Date(ts);
  let hr = String(date.getHours()).padStart(2, "0");
  let min = String(date.getMinutes()).padStart(2, "0");
  return `${hr}:${min}`;
}
</script>

<style></style>
