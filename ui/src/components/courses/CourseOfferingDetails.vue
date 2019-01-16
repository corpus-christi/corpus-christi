<template>
  <v-layout>
    <v-flex xs12 sm12>
      <v-card>
        <template v-if="pageLoaded">
          <v-container fill-height fluid>
            <v-flex xs9 sm9 align-end flexbox>
              <span class="headline">{{ courseOffering.title }}</span>
            </v-flex>
            <v-layout xs3 sm3 align-end justify-end>
              <v-btn flat color="primary" v-on:click="editCourseOffering(courseOffering)">
                <v-icon>edit</v-icon>&nbsp;{{ $t("actions.edit") }}
              </v-btn>
            </v-layout>
          </v-container>
          <v-card-text class="pa-4">
            <div>
              <b>Location: </b>
              <div class="multi-line ml-2">{{ displayLocation }}</div>
            </div>
            <div class="mt-2">{{ courseOffering.description }}</div>
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

    <!-- Edit dialog -->
    <v-dialog persistent scrollable v-model="courseOfferingDialog.show" max-width="500px">
      <CourseOfferingForm
        v-bind:editMode="courseOfferingDialog.editMode"
        v-bind:initialData="courseOfferingDialog.courseOffering"
        v-bind:saving="courseOfferingDialog.saving"
        v-on:cancel="cancelCourseOffering"
        v-on:save="saveCourseOffering"
      />
    </v-dialog>
  </v-layout>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  name: "CourseOfferingDetails",

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
        courseOffering: {},
        show: false,
        saveLoading: false
      },

      snackbar: {
        show: false,
        text: ""
      },
      pageLoaded: false
    };
  },
  props: {
    offeringId: 0
  },
  methods: {
    editCourseOffering(courseOffering) {
      this.courseOfferingDialog.courseOffering = JSON.parse(JSON.stringify(courseOffering));
      this.courseOfferingDialog.show = true;
    },

    cancelCourseOffering() {
      this.courseOfferingDialog.show = false;
    },

    saveCourseOffering(courseOffering) {
      this.courseOfferingDialog.saving = true;
      const courseOffering_id = courseOffering.id;

      // Locate the record we're updating in the table.
      const idx = this.courseOfferings.findIndex(c => c.id === courseOffering.id);
      // Get rid of the ID; not for consumption by endpoint.
      delete courseOffering.id;

      this.$http
        .patch(`/api/v1/courses/course_offerings/${courseOffering_id}`, courseOffering)
        .then(resp => {
          console.log("EDITED", resp);
          Object.assign(this.courseOfferings[idx], courseOffering);
          this.snackbar.text = this.$t("courses.updated");
          this.snackbar.show = true;
        })
        .catch(err => {
          console.error("FALURE", err.response);
          this.snackbar.text = this.$t("courses.update-failed");
          this.snackbar.show = true;
        })
        .finally(() => {
          this.courseOfferingDialog.show = false;
          this.courseOfferingDialog.saving = false;
        });
    },

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
