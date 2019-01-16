<template>
  <v-layout row wrap>
    <v-flex xs12>
      <v-btn
        outline
        color="primary"
        v-on:click="$router.push({ path: '/courses/all' })"
      ><v-icon>arrow_back</v-icon>{{ $t("actions.back") }}</v-btn>
    </v-flex>
    <v-flex sm12 md3>
      <v-card>
        <template v-if="loading">
          <v-container fill-height fluid>
            <v-layout xs12 align-center justify-center>
              <v-progress-circular indeterminate/>
            </v-layout>
          </v-container>
        </template>
        <template v-else>
          <v-card-title>
            <span class="headline">{{ course.name }}</span>
          </v-card-title>
          <v-card-text>
            {{ course.description }}
          </v-card-text>
        </template>
      </v-card>
    </v-flex>
    <v-flex sm12 md9 class="pl-2" v-if="!loading">
      <CourseOfferingsTable :course="course"/>
    </v-flex>
  </v-layout>
</template>

<script>
import CourseOfferingsTable from "./CourseOfferingsTable";
export default {
  name: "CourseDetails",
  components: {
    CourseOfferingsTable
  },
  props: {
    courseId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      course: {},
      loading: true,
      loadingFailed: false
    };
  },
  mounted() { 
    this.$http.get(`/api/v1/courses/courses/${this.courseId}`)
      .then(resp => {
        this.course = resp.data;
      })
      .catch(() => {
        this.loadingFailed = true;
      })
      .finally(() => {
        this.loading = false;
      });
  }
}
</script>

<style>

</style>
