<template>
  <v-layout>
    <v-flex xs12 sm12>
      <v-card>
        <template v-if="pageLoaded">
          <v-container fill-height fluid>
            <v-layout column>
              <v-flex xs9 sm9 align-end flexbox>
                <span class="headline">{{ courseOffering.course.name }}</span>
              </v-flex>
              <v-card-text class="pa-4">
                <b>{{ $t("courses.description") }}:</b>
                <div class="ml-2">{{ courseOffering.description }}</div>
                <b>{{ $t("courses.enrolled") }}:</b>
                <div class="ml-2">
                  {{ studentsAmt + " / " + courseOffering.maxSize }}
                </div>
              </v-card-text>
            </v-layout>
          </v-container>
        </template>
        <v-layout v-else justify-center height="500px">
          <div class="ma-5 pa-5">
            <v-progress-circular
              indeterminate
              color="primary"
            ></v-progress-circular>
          </div>
        </v-layout>
      </v-card>
    </v-flex>
  </v-layout>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  name: "CourseOfferingDetails",

  mounted() {
    this.pageLoaded = false;
    const id = this.offeringId;

    this.$http
      .get(`/api/v1/courses/course_offerings/${id}/students`)
      .then(resp => {
        //TODO make call in parent or Promise.all
        this.studentsAmt = resp.data.filter(student => student.active).length;
        this.$http.get(`/api/v1/courses/course_offerings/${id}`).then(resp => {
          this.courseOffering = resp.data;
        });
      });

    this.$http.get(`/api/v1/courses/course_offerings/${id}`).then(resp => {
      this.courseOffering = resp.data;
      this.pageLoaded = true;
    });
  },

  computed: {
    ...mapGetters(["currentLanguageCode"])
  },

  data() {
    return {
      courseOffering: {},
      courseOfferingDialog: {
        show: false,
        editMode: false,
        saving: false,
        courseOffering: {}
      },
      studentsAmt: 0,
      snackbar: {
        show: false,
        text: ""
      },
      pageLoaded: false
    };
  },
  props: {
    offeringId: null
  },
  methods: {
    getDisplayDate(ts) {
      let date = new Date(ts);
      return date.toLocaleTimeString(this.currentLanguageCode, {
        year: "numeric",
        month: "numeric",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      });
    },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    }
  }
};
</script>

<style scoped>
.multi-line {
  white-space: pre;
}
</style>
