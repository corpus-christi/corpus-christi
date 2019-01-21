<template>
  <v-container>
    <v-layout column>
      <v-flex>
        <v-card>
          <v-toolbar dark color="primary">
            <v-toolbar-title>{{
              $t("courses.dashboard.headers.course-attendance")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-sankey :data="courseAttendanceData" :settings="attendanceSankeySettings"></ve-sankey>
        </v-card>
      </v-flex>
      <v-flex>
        <v-card>
          <v-toolbar dark color="primary">
            <v-toolbar-title>{{
              $t("courses.dashboard.headers.enrollment")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-bar :data="courseData"></ve-bar>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
export default {
  name: "Dashboard",
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
            
            if (++enrollmentSubdataCount == resp.data.length /* FIXME: && graduationRateSubdataCount == resp.data.length */) {
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
          .get(`/api/v1/courses/course_offerings/${offering.id}/class_attendance`)
          .then(attendanceResp => {
            console.log("GOT ATTENDANCE SUBDATA", attendanceResp);
            attendanceResp.data.forEach(attendance => {
              attendance.attendance.forEach(student => {
                if (!attendanceData[student.studentId]) {
                  attendanceData[student.studentId] = 1;
                }
              });
              if (++attendanceSubdataCount == resp.data.length && enrollmentSubdataCount == resp.data.length && graduationRateSubdataCount == resp.data.length) {
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
            { status: "Course A", count: 32},
            { status: "Course B", count: 27},
            { status: "Course C", count: 29},
            { status: "Course D", count: 8},
            { status: "Course E", count: 4},
            { status: "Attended", count: 80 },
            { status: "Did Not Attend", count: 20 },
            { status: "Graduated", count: 75 },
            { status: "Did Not Graduate", count: 25 }
        ]
      },
      courseData: {
        columns: ["course", "enrollment", "graduationRate"],
        rows: []
      },
      attendanceSankeySettings: {
        links: [
            { source: "Course A", target: "Attended", value: 24 },
            { source: "Course A", target: "Did Not Attend", value: 8 },
            { source: "Course B", target: "Attended", value: 22 },
            { source: "Course B", target: "Did Not Attend", value: 5 },
            { source: "Course C", target: "Attended", value: 26 },
            { source: "Course C", target: "Did Not Attend", value: 3 },
            { source: "Course D", target: "Attended", value: 5 },
            { source: "Course D", target: "Did Not Attend", value: 3 },
            { source: "Course E", target: "Attended", value: 3 },
            { source: "Course E", target: "Did Not Attend", value: 1 },
            { source: "Attended", target: "Graduated", value: 75 },
            { source: "Attended", target: "Did Not Graduate", value: 5 },
            { source: "Did Not Attend", target: "Did Not Graduate", value: 20 }
        ],
        dataType: ["normal", "normal"]
      }
    };
  }
};
</script>
