<template>
  <v-container>
    <v-row wrap>
      <v-col cols="12" sm="6" md="6">
        <v-card>
          <v-toolbar class="pa-1">
            <v-toolbar-title>{{
              t("events.dashboard.headers.location-attendance")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-ring
            :data="locationAttendanceData"
            :legend-visible="false"
            align-center
          ></ve-ring>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="6">
        <v-card>
          <v-toolbar class="pa-1">
            <v-toolbar-title>{{
              t("events.dashboard.headers.home-group-percentage")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-liquidfill
            :data="homeGroupPercentageData"
            align-center
          ></ve-liquidfill>
        </v-card>
      </v-col>
      <v-col cols="12">
        <v-card>
          <v-toolbar class="pa-1">
            <v-toolbar-title>{{
              t("events.dashboard.headers.yearly-attendance")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-line
            :data="yearlyAttendanceData"
            :settings="attendanceLineSettings"
          ></ve-line>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import { useAuthStore } from "@/stores/auth";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const authStore = useAuthStore();

const locationAttendanceData = ref({
  columns: ["campus", "attendance"],
  rows: [] as any[]
});

const yearlyAttendanceData = ref({
  columns: ["date", "attendance"],
  rows: [] as any[]
});

const homeGroupPercentageData = ref({
  columns: ["homeGroups", "percent"],
  rows: [
    {
      homeGroups: t("events.dashboard.charts.home-groups"),
      percent: 0
    }
  ]
});

const attendanceLineSettings = ref({
  labelMap: {
    campus: t("events.dashboard.charts.campus"),
    attendance: t("events.dashboard.charts.attendance")
  }
});

watch(() => authStore.currentLocaleModel, () => {
  homeGroupPercentageData.value.rows[0].homeGroups = t("events.dashboard.charts.home-groups");
  attendanceLineSettings.value.labelMap.campus = t("events.dashboard.charts.campus");
  attendanceLineSettings.value.labelMap.attendance = t("events.dashboard.charts.attendance");
});

onMounted(() => {
  var today = new Date();
  var todayFormatted =
    today.getFullYear() + "-" + (today.getMonth() + 1) + "-" + today.getDate();
  var lastWeek = new Date();
  lastWeek.setDate(today.getDate() - 7);
  var lastWeekFormatted =
    lastWeek.getFullYear() + "-" + (lastWeek.getMonth() + 1) + "-" + lastWeek.getDate();

  http
    .get(`/api/v1/events/?include_participants=1&start=${lastWeekFormatted}&end=${todayFormatted}`)
    .then(resp => {
      console.log("GOT DATA", resp);
      var data: Record<string, number> = {};
      resp.data.forEach((event: any) => {
        var campus = "Unknown";
        var attendance = 0;
        if (event.location && event.location.description) {
          campus = event.location.description;
        }
        if (event.aggregate) {
          attendance = event.attendance;
        } else {
          attendance = event.participants.length;
        }
        if (!data[campus]) {
          data[campus] = 0;
        }
        data[campus] += attendance;
      });
      var arr: any[] = [];
      Object.keys(data).forEach(key => {
        arr.push({ campus: key, attendance: data[key] });
      });
      locationAttendanceData.value.rows = arr;
    })
    .catch(err => {
      console.error("GET FAILURE", err.response);
    });

  http
    .get(`/api/v1/events/?include_participants=1&sort=start`)
    .then(resp => {
      console.log("GOT DATA", resp);
      var data: Record<string, number> = {};
      for (let event of resp.data) {
        var date = event.start.slice(0, 10);
        var attendance = 0;
        if (event.attendance) {
          attendance = event.attendance;
        } else {
          attendance = event.participants.length;
        }
        if (!data[date]) {
          data[date] = 0;
        }
        data[date] += attendance;
      }
      var arr: any[] = [];
      Object.keys(data).forEach(date => {
        arr.push({ date: date, attendance: data[date] });
      });
      yearlyAttendanceData.value.rows = arr;

      http
        .get(`/api/v1/groups/members`)
        .then(resp => {
          console.log("GOT DATA", resp);
          homeGroupPercentageData.value.rows[0].percent = 0.5;
        })
        .catch(err => {
          console.error("GET FAILURE", err.response);
        });
    })
    .catch(err => {
      console.error("GET FAILURE", err.response);
    });
});
</script>
