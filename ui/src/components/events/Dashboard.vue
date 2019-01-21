<template>
  <v-container>
    <v-layout row wrap>
      <v-flex>
        <v-card>
          <v-toolbar dark color="primary">
            <v-toolbar-title>{{
              $t("events.dashboard.headers.location-attendance")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-ring :data="locationAttendanceData"></ve-ring>
        </v-card>
      </v-flex>
      <v-flex>
        <v-card>
          <v-toolbar dark color="primary">
            <v-toolbar-title>{{
              $t("events.dashboard.headers.home-group-percentage")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-liquidfill :data="homeGroupPercentageData"></ve-liquidfill>
        </v-card>
      </v-flex>
      <v-flex>
        <v-card>
          <v-toolbar dark color="primary">
            <v-toolbar-title>{{
              $t("events.dashboard.headers.yearly-attendance")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-line :data="yearlyAttendanceData"></ve-line>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
export default {
  name: "Dashboard",
  data: function() {
    // Get attendance data
    var today = new Date(); // eslint-disable-next-line
    var todayFormatted = today.getFullYear() + "-" + (today.getMonth() + 1) + "-" + today.getDate();
    var lastWeek = new Date();
    lastWeek.setDate(today.getDate() - 7); // eslint-disable-next-line
    var lastWeekFormatted = lastWeek.getFullYear() + "-" + (lastWeek.getMonth() + 1) + "-" + lastWeek.getDate();
    this.$http // eslint-disable-next-line
      .get(`/api/v1/events/?include_participants=1&start=${lastWeekFormatted}&end=${todayFormatted}`)
      .then(resp => {
        console.log("GOT DATA", resp);
        var data = Object();
        resp.data.forEach(event => {
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
        var arr = Array();
        Object.keys(data).forEach(key => {
          arr.push({
            campus: key,
            attendance: data[key]
          });
        });
        this.locationAttendanceData = {
          columns: ["campus", "attendance"],
          rows: arr
        };
      })
      .catch(err => {
        console.error("GET FALURE", err.response);
        this.showSnackbar(this.$t("dashboard.error-loading-data"));
        this.locationAttendanceData = {
          columns: [],
          rows: []
        };
      });
    this.$http
      .get(`/api/v1/events/?include_participants=1`)
      .then(resp => {
        var data = Object();
        var i;
        for (i = 0; i < resp.data.length; ++i) {
          var event = resp.data[i];
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
        var arr = Array();
        Object.keys(data).forEach(key => {
          arr.push({
            date: key,
            attendance: data[key]
          });
        });
        this.yearlyAttendanceData = {
          columns: ["date", "attendance"],
          rows: arr
        };
      })
      .catch(err => {
        console.error("GET FALURE", err.response);
        this.showSnackbar(this.$t("dashboard.error-loading-data"));
        this.yearlyAttendanceData = {
          columns: [],
          rows: []
        };
      });
    return {
      locationAttendanceData: {
        columns: [],
        rows: []
      },
      yearlyAttendanceData: {
        columns: [],
        rows: []
      },
      homeGroupPercentageData: {
        columns: ["homeGroups", "percent"],
        rows: [{
          homeGroups: "Home Groups",
          percent: 0.5
        }]
      }
    };
  }
}
</script>
