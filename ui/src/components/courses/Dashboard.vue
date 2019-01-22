<template>
  <v-container>
    <v-layout column>
      <v-flex>
        <v-card>
          <v-toolbar class="pa-1">
            <v-toolbar-title>{{
              $t("courses.dashboard.headers.course-retention")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-sankey
            :data="courseAttendanceData"
            :settings="attendanceSankeySettings"
          ></ve-sankey>
        </v-card>
      </v-flex>
      <v-flex>
        <v-card>
          <v-toolbar class="pa-1">
            <v-toolbar-title>{{
              $t("courses.dashboard.headers.course-success")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-bar :data="courseData" :settings="enrollmentBarSettings"></ve-bar>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
export default {
  name: "Dashboard",
  watch: {
    currentLocale() {
      this.enrollmentBarSettings.labelMap.course = this.$t("courses.dashboard.charts.course");
      this.enrollmentBarSettings.labelMap.enrollment = this.$t("courses.dashboard.charts.enrollment");
      this.enrollmentBarSettings.labelMap.graduationRate = this.$t("courses.dashboard.charts.graduation-rate");

      // TODO: Regenerate locale info for sankey
    }
  },
  computed: {
    ...mapState(["locales"]),
    ...mapGetters(["currentLocale"])
  },
  data: function() {
    var totalCourseEnrollment = 0;
    var totalStudentsAttended = 0;
    var totalStudentsGraduated = 0;

    var enrollmentData = Object();
    var graduationRateData = Object();
    var attendanceData = Object();
    var enrollmentSubdataCount = 0;
    var attendanceSubdataCount = 0;
    var graduationRateSubdataCount = 0; // TODO: Graduation rate API endpoints aren't done; finish later

    function enrollmentAndGraduationDataComplete(self) {
      Object.keys(enrollmentData).forEach(courseName => {
        totalCourseEnrollment += enrollmentData[courseName];
        var graduationRateValue = 0;
        if (graduationRateData[courseName]) {
          graduationRateValue = graduationRateData[courseName];
        }
        self.courseData.rows.push({
          course: courseName,
          enrollment: enrollmentData[courseName],
          graduationRate: graduationRateValue
        });
      });
    }

    function courseAttendanceDataComplete(self) {
      // TODO:
    }

    function courseFlowDataComplete(self) {
      // TODO:
    }

    this.$http
      .get(`/api/v1/courses/course_offerings`)
      .then(resp => {
        console.log("GOT DATA", resp);

        resp.data.forEach(offering => {
          var courseName = offering.course.name;
          if (!enrollmentData[courseName]) {
            enrollmentData[courseName] = 0;
          }
          if (!graduationRateData[courseName]) {
            graduationRateData[courseName] = 0;
          }

          this.$http
            .get(`/api/v1/courses/course_offerings/${offering.id}/students`)
            .then(studentResp => {
              console.log("GOT ENROLLMENT SUBDATA", studentResp);
              enrollmentData[courseName] += studentResp.data.length;

              if (
                ++enrollmentSubdataCount ==
                resp.data
                  .length /* FIXME: && graduationRateSubdataCount == resp.data.length */
              ) {
                enrollmentAndGraduationDataComplete(this);

                if (attendanceSubdataCount == resp.data.length) {
                  courseAttendanceDataComplete(this);
                }
              }
            })
            .catch(err => {
              console.error("GET FALURE", err.response);
            });

          /*this.$http
          .get(`/api/v1/courses/FIXME:`)
          .then(graduationResp => {
            // TODO:
          })
          .catch(err => {
            console.error("GET FALURE", err.response);
          });*/

          this.$http
            .get(
              `/api/v1/courses/course_offerings/${offering.id}/class_attendance`
            )
            .then(attendanceResp => {
              console.log("GOT ATTENDANCE SUBDATA", attendanceResp);
              attendanceResp.data.forEach(attendance => {
                attendance.attendance.forEach(student => {
                  if (!attendanceData[student.studentId]) {
                    attendanceData[student.studentId] = 1;
                  }
                });
                if (
                  ++attendanceSubdataCount == resp.data.length &&
                  enrollmentSubdataCount == resp.data.length &&
                  graduationRateSubdataCount == resp.data.length
                ) {
                  courseAttendanceDataComplete(this);
                }
              });
            })
            .catch(err => {
              console.error("GET FALURE", err.response);
            });
        });
      })
      .catch(err => {
        console.error("GET FALURE", err.response);
      });

    return {
      courseAttendanceData: {
        columns: ["status", "count"],
        rows: [
          { status: "Course A", count: 32 },
          { status: "Course B", count: 27 },
          { status: "Course C", count: 29 },
          { status: "Course D", count: 8 },
          { status: "Course E", count: 4 },
          { status: this.$t("courses.dashboard.charts.attended"), count: 80 },
          { status: this.$t("courses.dashboard.charts.did-not-attend"), count: 20 },
          { status: this.$t("courses.dashboard.charts.graduated"), count: 75 },
          { status: this.$t("courses.dashboard.charts.did-not-graduate"), count: 25 }
        ]
      },
      courseData: {
        columns: ["course", "enrollment", "graduationRate"],
        rows: []
      },
      attendanceSankeySettings: {
        links: [
          { source: "Course A", target: this.$t("courses.dashboard.charts.attended"), value: 24 },
          { source: "Course A", target: this.$t("courses.dashboard.charts.did-not-attend"), value: 8 },
          { source: "Course B", target: this.$t("courses.dashboard.charts.attended"), value: 22 },
          { source: "Course B", target: this.$t("courses.dashboard.charts.did-not-attend"), value: 5 },
          { source: "Course C", target: this.$t("courses.dashboard.charts.attended"), value: 26 },
          { source: "Course C", target: this.$t("courses.dashboard.charts.did-not-attend"), value: 3 },
          { source: "Course D", target: this.$t("courses.dashboard.charts.attended"), value: 5 },
          { source: "Course D", target: this.$t("courses.dashboard.charts.did-not-attend"), value: 3 },
          { source: "Course E", target: this.$t("courses.dashboard.charts.attended"), value: 3 },
          { source: "Course E", target: this.$t("courses.dashboard.charts.did-not-attend"), value: 1 },
          { source: this.$t("courses.dashboard.charts.attended"), target: this.$t("courses.dashboard.charts.graduated"), value: 75 },
          { source: this.$t("courses.dashboard.charts.attended"), target: this.$t("courses.dashboard.charts.did-not-graduate"), value: 5 },
          { source: this.$t("courses.dashboard.charts.did-not-attend"), target: this.$t("courses.dashboard.charts.did-not-graduate"), value: 20 }
        ],
        dataType: ["normal", "normal"]
      },
      enrollmentBarSettings: {
        labelMap: {
          course: this.$t("courses.dashboard.charts.course"),
          enrollment: this.$t("courses.dashboard.charts.enrollment"),
          graduationRate: this.$t("courses.dashboard.charts.graduation-rate")
        }
      }
    };
  }
};
</script>
