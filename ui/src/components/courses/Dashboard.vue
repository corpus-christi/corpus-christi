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
          <ve-sankey :data="courseFlowData" :loading="loadingCourseFlow" :settings="sankeySettings"></ve-sankey>
        </v-card>
      </v-flex>
      <v-flex>
        <v-card>
          <v-toolbar dark color="primary">
            <v-toolbar-title>{{
              $t("courses.dashboard.headers.enrollment")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-bar :data="courseData" :loading="loadingEnrollment"></ve-bar>
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
    this.$http
      .get(`/api/v1/courses/course_offerings`)
      .then(resp => {
        console.log("GOT DATA", resp);
        var courseData = Object();
        var graduationRateData = Object();
        var attendanceData = Object();
        var enrollmentSubdataCount = 0;
        var attendanceSubdataCount = 0;
        var graduationRateSubdataCount = 0; // TODO: Graduation rate API endpoints aren't done; finish later
        resp.data.forEach(offering => {
          var courseName = offering.course.name;
          if (!courseData[courseName]) {
            courseData[courseName] = 0;
          }
          if (!graduationRateData[courseName]) {
            graduationRateData[courseName] = 0;
          }
          
          this.$http
          .get(`/api/v1/courses/course_offerings/${offering.id}/students`)
          .then(studentResp => {
            console.log("GOT ENROLLMENT SUBDATA", studentResp);
            courseData[courseName] += studentResp.data.length;
            
            if (++enrollmentSubdataCount == resp.data.length /* FIXME: && graduationRateSubdataCount == resp.data.length */) {
              Object.keys(courseData).forEach(givenCourseName => {
                totalCourseEnrollment += courseData[givenCourseName];
                this.courseData.rows.push({
                  course: givenCourseName,
                  enrollment: courseData[givenCourseName],
                  graduationRate: graduationRateData[givenCourseName]
                });
              });
              this.loadingEnrollment = false;
            }
          })
          .catch(err => {
            console.error("GET FALURE", err.response);
          });

          this.$http
          .get(`/api/v1/courses/course_offerings/${offering.id}/class_attendance`)
          .then(attendanceResp => {
            console.log("GOT ATTENDANCE SUBDATA", attendanceResp);
            attendanceResp.data.forEach(attendance => {
              attendance.forEach(student => {
                if (!attendanceData[student.studentId]) {
                  attendanceData[student.studentId] = 1;
                }
              });
              if (++attendanceSubdataCount == resp.data.length /* FIXME: This might need another condition */) {
                // TODO: Handle completed sankey?
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
      courseData: {
        columns: ["course", "enrollment", "graduationRate"],
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
      loadingEnrollment: true,
      loadingCourseFlow: true
    };
  }
};
</script>
