<template>
  <v-container>
    <v-col>
      <v-col cols="12">
        <v-card>
          <v-toolbar class="pa-1">
            <v-toolbar-title>{{
              t("courses.dashboard.headers.course-retention")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-sankey
            :data="courseAttendanceData"
            :settings="attendanceSankeySettings"
          />
        </v-card>
      </v-col>
      <v-col cols="12">
        <v-card>
          <v-toolbar class="pa-1">
            <v-toolbar-title>{{
              t("courses.dashboard.headers.course-success")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-bar :data="courseData" :settings="enrollmentBarSettings" />
        </v-card>
      </v-col>
    </v-col>
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

const courseData = ref({
  columns: ["course", "enrolled", "graduated"],
  rows: [] as any[]
});

const courseAttendanceData = ref({
  columns: ["status", "count"],
  rows: [
    { status: "Course A", count: 32 },
    { status: "Course B", count: 27 },
    { status: "Course C", count: 29 },
    { status: "Course D", count: 8 },
    { status: "Course E", count: 4 },
    { status: t("courses.dashboard.charts.attended"), count: 80 },
    { status: t("courses.dashboard.charts.did-not-attend"), count: 20 },
    { status: t("courses.dashboard.charts.graduated"), count: 75 },
    { status: t("courses.dashboard.charts.did-not-graduate"), count: 25 }
  ]
});

const attendanceSankeySettings = ref({
  links: [
    { source: "Course A", target: t("courses.dashboard.charts.attended"), value: 24 },
    { source: "Course A", target: t("courses.dashboard.charts.did-not-attend"), value: 8 },
    { source: "Course B", target: t("courses.dashboard.charts.attended"), value: 22 },
    { source: "Course B", target: t("courses.dashboard.charts.did-not-attend"), value: 5 },
    { source: "Course C", target: t("courses.dashboard.charts.attended"), value: 26 },
    { source: "Course C", target: t("courses.dashboard.charts.did-not-attend"), value: 3 },
    { source: "Course D", target: t("courses.dashboard.charts.attended"), value: 5 },
    { source: "Course D", target: t("courses.dashboard.charts.did-not-attend"), value: 3 },
    { source: "Course E", target: t("courses.dashboard.charts.attended"), value: 3 },
    { source: "Course E", target: t("courses.dashboard.charts.did-not-attend"), value: 1 },
    { source: t("courses.dashboard.charts.attended"), target: t("courses.dashboard.charts.graduated"), value: 75 },
    { source: t("courses.dashboard.charts.attended"), target: t("courses.dashboard.charts.did-not-graduate"), value: 5 },
    { source: t("courses.dashboard.charts.did-not-attend"), target: t("courses.dashboard.charts.did-not-graduate"), value: 20 }
  ],
  dataType: ["normal", "normal"]
});

const enrollmentBarSettings = ref({
  labelMap: {
    course: t("courses.dashboard.charts.course"),
    enrolled: t("courses.dashboard.charts.enrolled"),
    graduated: t("courses.dashboard.charts.graduated")
  }
});

watch(() => authStore.currentLocaleModel, () => {
  enrollmentBarSettings.value.labelMap.course = t("courses.dashboard.charts.course");
  enrollmentBarSettings.value.labelMap.enrolled = t("courses.dashboard.charts.enrolled");
  enrollmentBarSettings.value.labelMap.graduated = t("courses.dashboard.charts.graduated");
});

onMounted(() => {
  let enrollmentData: Record<string, number> = {};
  let graduationData: Record<string, number> = {};
  let enrollmentSubdataCount = 0;
  let attendanceSubdataCount = 0;
  let graduationSubdataCount = 0;

  function enrollmentAndGraduationDataComplete() {
    Object.keys(enrollmentData).forEach(courseName => {
      let graduationValue = 0;
      if (graduationData[courseName]) {
        graduationValue = graduationData[courseName];
      }
      courseData.value.rows.push({
        course: courseName,
        enrolled: enrollmentData[courseName],
        graduated: graduationValue === 0 ? graduationValue : 20
      });
    });
  }

  http
    .get(`/api/v1/courses/course_offerings`)
    .then(resp => {
      resp.data.forEach((offering: any) => {
        var courseName = offering.course.name;
        if (!enrollmentData[courseName]) {
          enrollmentData[courseName] = 0;
        }
        if (!graduationData[courseName]) {
          graduationData[courseName] = 0;
        }

        http
          .get(`/api/v1/courses/course_offerings/${offering.id}/students`)
          .then(studentResp => {
            enrollmentData[courseName] += studentResp.data.length;

            if (++enrollmentSubdataCount === resp.data.length) {
              enrollmentAndGraduationDataComplete();
            }
          })
          .catch(err => {
            console.error("GET FAILURE", err.response);
          });

        http
          .get(`/api/v1/courses/course_offerings/${offering.id}/class_attendance`)
          .then(attendanceResp => {
            attendanceResp.data.forEach((attendance: any) => {
              attendance.attendance.forEach((student: any) => {
                // track attendance
              });
              attendanceSubdataCount++;
            });
          })
          .catch(err => {
            console.error("GET FAILURE", err.response);
          });
      });
    })
    .catch(err => {
      console.error("GET FAILURE", err.response);
    });
});
</script>
