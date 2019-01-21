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
              $t("courses.dashboard.headers.graduation-rate")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-line :data="graduationRateData" :loading="loadingGraduationRate"></ve-line>
        </v-card>
      </v-flex>
      <v-flex>
        <v-card>
          <v-toolbar dark color="primary">
            <v-toolbar-title>{{
              $t("courses.dashboard.headers.enrollment")
            }}</v-toolbar-title>
          </v-toolbar>
          <ve-bar :data="enrollmentData" :loading="loadingEnrollment"></ve-bar>
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
      .get(`/api/v1/courses/course_offerings`)
      .then(resp => {
        console.log("GOT DATA", resp);
        var enrollmentData = Object();
        var graduationRateData = Object();
        var subdataCount = 0;
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
            console.log("GOT SUBDATA", studentResp);
            enrollmentData[courseName] += studentResp.data.length;
            
            if (++subdataCount == resp.data.length) {
              Object.keys(enrollmentData).forEach(givenCourseName => {
                this.enrollmentData.rows.push({
                  course: givenCourseName,
                  enrollment: enrollmentData[givenCourseName]
                });
              });
              this.loadingEnrollment = false;
            }
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
      graduationRateData: {
        columns: [],
        rows: []
      },
      enrollmentData: {
        columns: ["course", "enrollment"],
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
      loadingGraduationRate: true,
      loadingCourseFlow: true
    };
  }
};
</script>
