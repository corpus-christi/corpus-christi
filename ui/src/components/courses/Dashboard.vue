<template>
  <v-container>
    <v-layout row wrap>
      <v-flex>
        <v-card>
          <v-toolbar dark color="primary">
            <v-toolbar-title>{{
              $t("courses.dashboard.headers.course-flow")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-sankey :data="courseFlowData" :loading="loading" :settings="sankeySettings"></ve-sankey>
        </v-card>
      </v-flex>
      <v-flex>
        <v-card>
          <v-toolbar dark color="primary">
            <v-toolbar-title>{{
              $t("courses.dashboard.headers.graduation-rate")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-line :data="graduationRateData" :loading="loading"></ve-line>
        </v-card>
      </v-flex>
      <v-flex>
        <v-card>
          <v-toolbar dark color="primary">
            <v-toolbar-title>{{
              $t("courses.dashboard.headers.enrollment")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-bar :data="enrollmentData" :loading="loading"></ve-bar>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
export default {
  name: "Dashboard",
  data: function() {
    this.$http
      .get(`/api/v1/courses/courses`)
      .then(resp => {
          console.log(resp);
          // TODO FIXME Data collection goes here
      })
      .catch(err => {
        console.error("GET FALURE", err.response);
        this.showSnackbar(this.$t("dashboard.error-loading-data"));
        this.graduationRateData = {
          columns: [],
          rows: []
        };
        this.enrollmentData = {
          columns: [],
          rows: []
        };
        this.courseFlowData = {
          columns: [],
          rows: []
        };
      })
    return {
      courseFlowData: {
        columns: ["status", "count"],
        rows: [
            { status: "Enrolled", count: 100 },
            { status: "Attended", count: 80 },
            { status: "Did Not Attend", count: 20 },
            { status: "Graduated", count: 72 },
            { status: "Did Not Graduate", count: 18 }
        ]
      },
      graduationRateData: {
        columns: [], // NOTE: dynamically generate columns based on courses
        rows: []
      },
      enrollmentData: {
        columns: [], // NOTE: dynamically generate columns based on courses
        rows: []
      },
      sankeySettings: {
        links: [
            { source: "Enrolled", target: "Attended", value: 0.8 },
            { source: "Enrolled", target: "Did Not Attend", value: 0.2 },
            { source: "Attended", target: "Graduated", value: 0.9 },
            { source: "Attended", target: "Did Not Graduate", value: 0.1 },
            { source: "Did Not Attend", target: "Did Not Graduate", value: 1 }
        ],
        dataType: ["normal", "percent"]
      },
      loading: true
    };
  }
};
</script>
