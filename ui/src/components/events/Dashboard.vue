<template>
  <v-container>
    <v-layout row wrap>
      <v-flex xs12 sm6 md6 lg6 xl6>
        <v-card>
          <v-toolbar class="pa-1">
            <v-toolbar-title>{{
              $t("events.dashboard.headers.location-attendance")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-ring
            :data="locationAttendanceData"
            :legend-visible="false"
            align-center
          ></ve-ring>
        </v-card>
      </v-flex>
      <v-flex xs12 sm6 md6 lg6 xl6>
        <v-card>
          <v-toolbar class="pa-1">
            <v-toolbar-title>{{
              $t("events.dashboard.headers.home-group-percentage")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-liquidfill
            :data="homeGroupPercentageData"
            align-center
          ></ve-liquidfill>
        </v-card>
      </v-flex>
      <v-flex xs12 sm12 md12 lg12 xl12>
        <v-card>
          <v-toolbar class="pa-1">
            <v-toolbar-title>{{
              $t("events.dashboard.headers.yearly-attendance")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-line
            :data="yearlyAttendanceData"
            :settings="attendanceLineSettings"
          ></ve-line>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapGetters, mapState } from "vuex";
export default {
  name: "Dashboard",
  watch: {
    currentLocale() {
      this.homeGroupPercentageData.rows[0].homeGroups = this.$t(
        "events.dashboard.charts.home-groups"
      );
      this.attendanceLineSettings.labelMap.campus = this.$t(
        "events.dashboard.charts.campus"
      );
      this.attendanceLineSettings.labelMap.attendance = this.$t(
        "events.dashboard.charts.attendance"
      );
    }
  },
  computed: {
    ...mapState(["locales"]),
    ...mapGetters(["currentLocale"])
  },
  data: function() {
    // Get attendance data
    var today = new Date();
    var todayFormatted =
      today.getFullYear() +
      "-" +
      (today.getMonth() + 1) +
      "-" +
      today.getDate();
    var lastWeek = new Date();
    lastWeek.setDate(today.getDate() - 7);
    var lastWeekFormatted =
      lastWeek.getFullYear() +
      "-" +
      (lastWeek.getMonth() + 1) +
      "-" +
      lastWeek.getDate();
    this.$http
      .get(
        `/api/v1/events/?include_participants=1&start=${lastWeekFormatted}&end=${todayFormatted}`
      )
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
        this.locationAttendanceData.rows = arr;
      })
      .catch(err => {
        console.error("GET FALURE", err.response);
      });

    // Get historic attendance data
    this.$http
      .get(`/api/v1/events/?include_participants=1&sort=start`)
      .then(resp => {
        console.log("GOT DATA", resp);
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
        Object.keys(data).forEach(date => {
          arr.push({
            date: date,
            attendance: data[date]
          });
        });
        this.yearlyAttendanceData.rows = arr;

        // Get home group membership data
        this.$http
          .get(`/api/v1/groups/members`)
          .then(resp => {
            console.log("GOT DATA", resp);
            this.homeGroupPercentageData.rows[0].percent = 0.5;
            // resp.data.length / arr[arr.length - 1].attendance;
            this.loading = false;
          })
          .catch(err => {
            console.error("GET FALURE", err.response);
          });
      })
      .catch(err => {
        console.error("GET FALURE", err.response);
      });

    // Make these data structures available as part of `this`
    return {
      locationAttendanceData: {
        columns: ["campus", "attendance"],
        rows: []
      },
      yearlyAttendanceData: {
        columns: ["date", "attendance"],
        rows: []
      },
      homeGroupPercentageData: {
        columns: ["homeGroups", "percent"],
        rows: [
          {
            homeGroups: this.$t("events.dashboard.charts.home-groups"),
            percent: 0
          }
        ]
      },
      attendanceLineSettings: {
        labelMap: {
          campus: this.$t("events.dashboard.charts.campus"),
          attendance: this.$t("events.dashboard.charts.attendance")
        }
      }
    };
  }
};
</script>
