<template>
  <div>
    <v-layout row wrap>
      <v-flex xs12>
        <v-btn
          outline
          color="primary"
          v-on:click="$router.push({ name: 'all-courses' })"
          ><v-icon>arrow_back</v-icon>{{ $t("actions.back") }}</v-btn
        >
      </v-flex>
      <v-flex sm12 md3>
        <v-card>
          <template v-if="loading">
            <v-container fill-height fluid>
              <v-layout xs12 align-center justify-center>
                <v-progress-circular color="primary" indeterminate />
              </v-layout>
            </v-container>
          </template>
          <template v-else>
            <v-card-title class="d-block">
              <h5 class="headline">{{ course.name }}</h5>
              <span class="caption" v-if="!course.active">
                <v-icon small>archive</v-icon>
                {{ $t("courses.is-archived") }}
              </span>
            </v-card-title>
            <v-card-text> {{ course.description }} </v-card-text>
            <v-card-actions>
              <v-btn
                flat
                color="primary"
                @click="editCourse"
                data-cy="course-details-edit-button"
              >
                <v-icon left>edit</v-icon>
                {{ $t("actions.edit") }}
              </v-btn>
            </v-card-actions>
          </template>
        </v-card>
        <v-card class="mt-2" v-if="!loading">
          <template v-if="course.prerequisites.length > 0">
            <v-card-title>
              <h5 class="headline">{{ $t("courses.prerequisites") }}</h5>
            </v-card-title>
            <v-card-text>
              <v-list dense>
                <v-list-tile
                  v-for="prereq of course.prerequisites"
                  :key="prereq.id"
                  :to="{
                    name: 'course-details',
                    params: { courseId: prereq.id }
                  }"
                >
                  {{ prereq.name }}
                </v-list-tile>
              </v-list>
            </v-card-text>
          </template>
          <template v-else>
            <v-card-text> {{ $t("courses.no-prerequisites") }} </v-card-text>
          </template>
        </v-card>
      </v-flex>
      <v-flex sm12 md9 class="pl-2" v-if="!loading">
        <CourseOfferingsTable :course="course" />
      </v-flex>
    </v-layout>

    <v-dialog
      v-model="courseDialog.show"
      max-width="500px"
      persistent
      scrollable
      data-cy="course-editor"
    >
      <CourseEditor
        :editMode="true"
        :initialData="courseDialog.course"
        @cancel="cancelCourse"
        @save="saveCourse"
      />
    </v-dialog>

    <v-snackbar v-model="snackbar.show" data-cy="courses-table-snackbar">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false">{{
        $t("actions.close")
      }}</v-btn>
    </v-snackbar>
  </div>
</template>

<script>
import CourseOfferingsTable from "./CourseOfferingsTable";
import CourseEditor from "./CourseEditor";
export default {
  name: "CourseDetails",
  components: {
    CourseOfferingsTable,
    CourseEditor
  },
  props: {
    courseId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      course: { prerequisites: [] },
      loading: true,
      loadingFailed: false,
      courseDialog: {
        show: false,
        course: {}
      },
      snackbar: {
        show: false,
        text: ""
      }
    };
  },
  mounted() {
    this.loadCourse();
  },
  watch: {
    $route: "loadCourse"
  },
  methods: {
    loadCourse() {
      this.loading = true;
      this.loadingFailed = false;
      this.$http
        .get(`/api/v1/courses/courses/${this.courseId}`)
        .then(resp => {
          this.course = resp.data;
        })
        .catch(() => {
          this.loadingFailed = true;
        })
        .finally(() => {
          this.loading = false;
        });
    },

    editCourse() {
      this.courseDialog.course = { ...this.course };
      this.courseDialog.show = true;
    },

    cancelCourse() {
      this.courseDialog.show = false;
    },

    saveCourse(course) {
      if (course instanceof Error) {
        this.snackbar.text = this.$t("courses.update-failed");
      } else {
        Object.assign(this.course, course);
      }
      this.snackbar.text = this.$t("courses.updated");
      this.snackbar.show = true;
      this.courseDialog.show = false;
    }
  }
};
</script>

<style></style>
