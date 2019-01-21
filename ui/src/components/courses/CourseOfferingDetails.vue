<template>
  <v-layout>
    <v-flex xs12 sm12>
      <v-card>
        <template v-if="pageLoaded">
          <v-container fill-height fluid>
            <v-flex xs9 sm9 align-end flexbox>
              <span class="headline">{{ courseOffering.course.name }}</span>
            </v-flex>
          </v-container>
          <v-card-text class="pa-4">
            <b>{{ $t("courses.description") }}:</b>
            <div class="ml-2">{{ courseOffering.description }}</div>
            <b>{{ $t("courses.enrolled") }}:</b>
            <div class="ml-2">{{ "0 / " + courseOffering.maxSize }}</div>
          </v-card-text>
          <v-card-actions>
            <v-btn
              flat
              ripple
              color="primary"
              v-on:click="navigateTo('/participants')"
            >
              <v-icon>person</v-icon>&nbsp;{{ $t("events.participants.title") }}
            </v-btn>
          </v-card-actions>
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
import CourseOfferingForm from "./CourseOfferingForm";

export default {
  name: "CourseOfferingDetails",
  components: {
    CourseOfferingForm
  },

  mounted() {
    this.pageLoaded = false;
    const id = this.offeringId;
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

      snackbar: {
        show: false,
        text: ""
      },
      pageLoaded: false
    };
  },
  props: {
    offeringId: 0,
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

    navigateTo(path) {
      this.$router.push({
        path: "/courses/" + offeringId + path
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
