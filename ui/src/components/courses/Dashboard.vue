<template>
  <v-container>
    <v-layout column>
      <v-flex xs12 sm12 md12 lg12 xl12>
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
      <v-flex xs12 sm12 md12 lg12 xl12>
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
import { mapGetters, mapState } from "vuex";
export default {
  name: "Dashboard",
  watch: {
    currentLocale() {
      this.enrollmentBarSettings.labelMap.course = this.$t(
        "courses.dashboard.charts.course"
      );
      this.enrollmentBarSettings.labelMap.enrolled = this.$t(
        "courses.dashboard.charts.enrolled"
      );
      this.enrollmentBarSettings.labelMap.graduated = this.$t(
        "courses.dashboard.charts.graduated"
      );

      // TODO: Regenerate locale info for sankey
    }
  },
  computed: {
    ...mapState(["locales"]),
    ...mapGetters(["currentLocale"])
  },
  data: function() {
    var totalCourseEnrollment = 0; // eslint-disable-line
    var totalStudentsAttended = 0; // eslint-disable-line
    var totalStudentsGraduated = 0; // eslint-disable-line

    var enrollmentData = Object();
    var graduationData = Object();
    var attendanceData = Object();
    var enrollmentSubdataCount = 0;
    var attendanceSubdataCount = 0;
    var graduationSubdataCount = 0; // TODO: Graduation rate API endpoints aren't done; finish later

    function enrollmentAndGraduationDataComplete(self) {
      Object.keys(enrollmentData).forEach(courseName => {
        totalCourseEnrollment += enrollmentData[courseName]; // eslint-disable-next-line
        var graduationValue = 0; // eslint-disable-next-line
        if (graduationData[courseName]) {
          graduationValue = graduationData[courseName]; // eslint-disable-next-line
        }
        self.courseData.rows.push({
          course: courseName,
          enrolled: enrollmentData[courseName],
          graduated: graduationValue == 0 ? graduationValue : 20 // FIXME: graduationValue
        });
      });
    }

    function courseAttendanceDataComplete(/* self */) {
      // eslint-disable-line
      // TODO:
    }

    /*
    function courseFlowDataComplete(self) {
      // eslint-disable-line
      // TODO:
    }
     */

    // Get course data
    this.$http
      .get(`/api/v1/courses/course_offerings`)
      .then(resp => {
        console.log("GOT DATA", resp);

        resp.data.forEach(offering => {
          var courseName = offering.course.name;
          if (!enrollmentData[courseName]) {
            enrollmentData[courseName] = 0;
          }
          if (!graduationData[courseName]) {
            graduationData[courseName] = 0;
          }

          // Get enrollment data
          this.$http
            .get(`/api/v1/courses/course_offerings/${offering.id}/students`)
            .then(studentResp => {
              console.log("GOT ENROLLMENT SUBDATA", studentResp);
              enrollmentData[courseName] += studentResp.data.length;

              if (
                ++enrollmentSubdataCount == resp.data.length
                /* FIXME: && graduationSubdataCount == resp.data.length */
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

          // Get graduation data
          /*this.$http
          .get(`/api/v1/courses/FIXME:`)
          .then(graduationResp => {
            // TODO:
          })
          .catch(err => {
            console.error("GET FALURE", err.response);
          });*/

          // Get attendance data
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
                  graduationSubdataCount == resp.data.length
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
          {
            status: this.$t("courses.dashboard.charts.did-not-attend"),
            count: 20
          },
          { status: this.$t("courses.dashboard.charts.graduated"), count: 75 },
          {
            status: this.$t("courses.dashboard.charts.did-not-graduate"),
            count: 25
          }
        ]
      },
      courseData: {
        columns: ["course", "enrolled", "graduated"],
        rows: []
      },
      attendanceSankeySettings: {
        links: [
          // NOTE: This is stub data and should be changed
          {
            source: "Course A",
            target: this.$t("courses.dashboard.charts.attended"),
            value: 24
          },
          {
            source: "Course A",
            target: this.$t("courses.dashboard.charts.did-not-attend"),
            value: 8
          },
          {
            source: "Course B",
            target: this.$t("courses.dashboard.charts.attended"),
            value: 22
          },
          {
            source: "Course B",
            target: this.$t("courses.dashboard.charts.did-not-attend"),
            value: 5
          },
          {
            source: "Course C",
            target: this.$t("courses.dashboard.charts.attended"),
            value: 26
          },
          {
            source: "Course C",
            target: this.$t("courses.dashboard.charts.did-not-attend"),
            value: 3
          },
          {
            source: "Course D",
            target: this.$t("courses.dashboard.charts.attended"),
            value: 5
          },
          {
            source: "Course D",
            target: this.$t("courses.dashboard.charts.did-not-attend"),
            value: 3
          },
          {
            source: "Course E",
            target: this.$t("courses.dashboard.charts.attended"),
            value: 3
          },
          {
            source: "Course E",
            target: this.$t("courses.dashboard.charts.did-not-attend"),
            value: 1
          },
          {
            source: this.$t("courses.dashboard.charts.attended"),
            target: this.$t("courses.dashboard.charts.graduated"),
            value: 75
          },
          {
            source: this.$t("courses.dashboard.charts.attended"),
            target: this.$t("courses.dashboard.charts.did-not-graduate"),
            value: 5
          },
          {
            source: this.$t("courses.dashboard.charts.did-not-attend"),
            target: this.$t("courses.dashboard.charts.did-not-graduate"),
            value: 20
          }
        ],
        dataType: ["normal", "normal"]
      },
      enrollmentBarSettings: {
        labelMap: {
          course: this.$t("courses.dashboard.charts.course"),
          enrolled: this.$t("courses.dashboard.charts.enrolled"),
          graduated: this.$t("courses.dashboard.charts.graduated")
        }
      }
    };
  }
};
</script>
