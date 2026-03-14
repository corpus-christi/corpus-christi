<template>
  <div>
    <vue-cal
      :locale="authStore.currentLocaleModel?.code?.split('-')[0]"
      default-view="week"
      events-on-month-view
      :events="calendarEvents"
      v-on:event-focus="goToEvent"
    >
    </vue-cal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import Vuecal from "vue-cal";
import "vue-cal/dist/vuecal.css";
import { useAuthStore } from "@/stores/auth";

const http = inject<AxiosInstance>("$http")!;
const router = useRouter();
const authStore = useAuthStore();

const events = ref<any[]>([]);

const calendarEvents = computed(() => events.value);

function getDatetime(ts: any) {
  let date = getDateFromTimestamp(ts);
  let time = getTimeFromTimestamp(ts);
  return `${date} ${time}`;
}

function getTemplate(event: any) {
  return `<span data-cy="cal-event-${event.id}">${event.title}</span>`;
}

function goToEvent(e: any) {
  router.push({ path: "/event/" + e.event.id + "/details" });
}

function getDateFromTimestamp(ts: any) {
  let date = new Date(ts);
  if (date.getTime() < 86400000) {
    return "";
  }
  let yr = date.toLocaleDateString(authStore.currentLanguageCode, { year: "numeric" });
  let mo = date.toLocaleDateString(authStore.currentLanguageCode, { month: "2-digit" });
  let da = date.toLocaleDateString(authStore.currentLanguageCode, { day: "2-digit" });
  return `${yr}-${mo}-${da}`;
}

function getTimeFromTimestamp(ts: any) {
  let date = new Date(ts);
  let hr = String(date.getHours()).padStart(2, "0");
  let min = String(date.getMinutes()).padStart(2, "0");
  return `${hr}:${min}`;
}

onMounted(() => {
  http.get("/api/v1/events/").then(resp => {
    var currentDate = new Date();
    for (let event of resp.data) {
      events.value.push({
        event: event,
        start: getDatetime(event.start),
        end: getDatetime(event.end),
        description: event.description,
        class: new Date(event.end) < currentDate ? "leisure" : "sport",
        content: getTemplate(event)
      });
    }
  });
});
</script>

<style>
.vuecal__event.sport {
  background-color: rgba(253, 150, 53, 0.9);
  border: 1px solid rgb(230, 150, 53);
  color: #fff;
}
.vuecal__event.leisure {
  background-color: rgba(158, 158, 158, 0.8);
  border: 1px solid rgb(158, 158, 158);
  color: #fff;
}

.vuecal__menu,
.vuecal__cell-events-count {
  background-color: #e69635;
}
.vuecal__menu li {
  border-bottom-color: #fff;
  color: #fff;
}
.vuecal__menu li.active {
  background-color: rgba(255, 255, 255, 0.15);
}
.vuecal__title {
  background-color: rgba(230, 150, 53, 0.5);
}
.vuecal__cell.today,
.vuecal__cell.current {
  background-color: rgba(240, 240, 255, 0.4);
}
.vuecal:not(.vuecal--day-view) .vuecal__cell.selected {
  background-color: rgba(230, 150, 53, 0.1);
}
.vuecal__cell.selected:before {
  border-color: rgba(230, 150, 53, 0.5);
}
</style>
