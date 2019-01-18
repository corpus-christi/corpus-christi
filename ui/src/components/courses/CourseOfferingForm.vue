<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <!-- description -->
        <v-textarea
          v-model="courseOffering.description"
          v-bind:label="$t('courses.description')"
          name="description"
          rows="3"
          data-cy="course-offering-description"
        ></v-textarea>

        <!-- date -->
        <v-layout>
          <v-flex xs12 md7>
            <v-menu
              ref="dateMenu"
              v-model="showDatePicker"
              :close-on-content-click="false"
              :nudge-right="40"
              :return-value.sync="dates"
              lazy
              transition="scale-transition"
              offset-y
              full-width
              min-width="290px"
            >
              <v-combobox
                slot="activator"
                v-model="dates"
                multiple
                chips
                small-chips
                v-bind:label="$t('courses.dates')"
                prepend-icon="event"
                readonly
                data-cy="course-offering-date"
              ></v-combobox>
              <v-date-picker 
                v-model="dates" 
                multiple no-title scrollable 
                v-bind:locale="currentLanguageCode"
                data-cy="course-offering-date-picker"
              >
                <v-spacer></v-spacer>
                <v-btn
                  flat
                  color="primary"
                  @click="showDatePicker = false"
                  data-cy="course-offering-date-cancel"
                >{{ $t("actions.cancel") }}</v-btn>
                <v-btn
                  flat
                  color="primary"
                  @click="$refs.dateMenu.save(dates)"
                  data-cy="course-offering-date-ok"
                >{{ $t("actions.confirm") }}</v-btn>
              </v-date-picker>
            </v-menu>
          </v-flex>
          
          <!-- time -->
          <v-flex xs12 md4 ml-4>
            <v-menu
              ref="timeMenu"
              v-model="showTimePicker"
              :close-on-content-click="false"
              :nudge-right="40"
              :return-value.sync="time"
              lazy
              transition="scale-transition"
              offset-y
              full-width
              min-width="290px"
            >
              <v-text-field
                slot="activator"
                v-model="time"
                v-bind:label="$t('courses.choose-time')"
                prepend-icon="schedule"
                readonly
                data-cy="course-offering-time"
              ></v-text-field>
              <v-time-picker
                v-if="showTimePicker"
                :format="timeFormat"
                v-model="time"
                data-cy="course-offering-time-picker"
              >
                <v-spacer></v-spacer>
                <v-btn
                  flat
                  color="primary"
                  @click="showTimePicker = false"
                  data-cy="course-offering-time-cancel"
                >{{ $t("actions.cancel") }}</v-btn>
                <v-btn
                  flat
                  color="primary"
                  @click="$refs.timeMenu.save(time)"
                  data-cy="course-offering-time-ok"
                >{{ $t("actions.confirm") }}</v-btn>
              </v-time-picker>
            </v-menu>
        </v-flex>
        </v-layout>
       
        <!-- teacher -->
        <v-text-field
          v-model="teacher"
          v-bind:label="$t('courses.choose-teacher')"
          name="teacher"
          data-cy="course-offering-teacher"
        ></v-text-field>

        <!-- location -->
        <v-text-field
          v-model="location"
          v-bind:label="$t('courses.choose-location')"
          name="location"
          data-cy="course-offering-location"
        ></v-text-field>

        <!-- max size TODO: integer validation-->
        <v-flex xs7 md7>
          <v-text-field
            v-model="courseOffering.maxSize"
            v-bind:label="$t('courses.max-size')"
            name="max-size"
            type="number"
            v-validate="'integer'"
            data-cy="course-offering-max-size"
          ></v-text-field>
        </v-flex>
      </form>
    </v-card-text>
    <v-card-actions>
      <v-btn
        color="secondary"
        flat
        :disabled="saving"
        v-on:click="cancel"
      >{{ $t("actions.cancel") }}</v-btn>
      <v-spacer></v-spacer>
      <v-btn color="primary" flat :disabled="saving" v-on:click="clear">{{ $t("actions.clear") }}</v-btn>
      <v-btn
        color="primary"
        raised
        :disabled="saving"
        :loading="saving"
        v-on:click="save"
      >{{ $t("actions.save") }}</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>

import { isEmpty, cloneDeep } from "lodash";
import { mapGetters } from "vuex";

export default {
  name: "CourseOfferingForm",
  data: function() {
    return {
      availableCourses: [],
      location: "",
      teacher: "",
      time: "",
      dates: [],
      saving: false,

      showDatePicker: false,
      showTimePicker: false,

      courseOffering: {},
    };
  },
  computed: {
    title() {
      return this.editMode ? this.$t("actions.edit") : this.$t("courses.new-offering");
    },

    timeFormat() {
      if (this.currentLanguageCode == "en") {
        return "ampm";
      } else return "24hr";
    },

    today() {
      return this.getDateFromTimestamp(Date.now());
    },
    
    ...mapGetters(["currentLanguageCode"])
  },

  watch: {
    // Make sure data stays in sync with any changes to `initialData` from parent.
    initialData(courseProp) {
      if (isEmpty(courseProp)) {
        this.clear();
      } else {
        this.courseOffering = courseProp;
        if (this.courseOffering.when != null) {
          this.courseOffering.when = new Date(this.courseOffering.when);
          this.startTime = this.getTimeFromTimestamp(this.courseOffering.when);
          this.startDate = this.getDateFromTimestamp(this.courseOffering.when);
        }
      }
    }
  },

  props: {
    editMode: {
      type: Boolean,
      required: true
    },
    initialData: {
      type: Object,
      required: true
    },
    course: {
      type: Object,
      required: true
    }
  },

  methods: {
     // Abandon ship.
    cancel() {
      this.clear();
      this.$emit("cancel");
    },

    // Clear the forms.
    clear() {
      this.courseOffering = {};
      this.time = "";
      this.date = "";
      this.showDatePicker = false;
      this.timeModal = false;
      this.dates = [];
      
      this.$validator.reset();
    },

    // Save the record and trigger a save event, returning the updated `Course Offering`.
    save() {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          this.saving = true;
          let courseOffering = cloneDeep(this.courseOffering);
          courseOffering.courseId = this.course.id;
          this.saveCourseOffering(courseOffering);
        }
      });
    },

    saveCourseOffering(courseOffering) {
      if (this.editMode) {
        // Hang on to the ID of the record being updated.
        const courseOfferingId = courseOffering.id;

        // Get rid of the ID; not for consumption by endpoint.
        delete courseOffering.id;

        this.$http
          .patch(`/api/v1/courses/course_offerings/${courseOfferingId}`, courseOffering)
          .then(resp => {
            console.log("EDITED", resp);
            courseOffering = resp.data;
            this.$emit("save", courseOffering);
          })
          .catch(err => {
            console.error("FALURE", err.response);
            this.$emit("save", err);
          })
          .finally(() => {
            this.saving = false;
          });
      } else {
        courseOffering.active = true;
        this.$http
          .post("/api/v1/courses/course_offerings", courseOffering)
          .then(resp => {
            console.log("ADDED", resp);
            courseOffering = resp.data;
            this.$emit("save", courseOffering);
          })
          .catch(err => {
            console.error("FAILURE", err.response);
            this.$emit("save", courseOffering);
          })
          .finally(() => {
            this.saving = false;
          });
      }
    },

    remove(item) {
      this.prereqs.splice(this.prereqs.indexOf(item), 1);
      this.prereqs = [...this.prereqs];
    },

    getTimestamp(date, time) {
      let datems = new Date(date).getTime();
      let timearr = time.split(":");
      let timemin = Number(timearr[0]) * 60 + Number(timearr[1]);
      let timems = timemin * 60000;
      let tzoffset = new Date().getTimezoneOffset() * 60000;
      return new Date(datems + timems + tzoffset);
    },

    getDateFromTimestamp(ts) {
      let date = new Date(ts);
      if (date.getTime() < 86400000) {
        //ms in a day
        return "";
      }
      let yr = date.toLocaleDateString(this.currentLanguageCode, {
        year: "numeric"
      });
      let mo = date.toLocaleDateString(this.currentLanguageCode, {
        month: "2-digit"
      });
      let da = date.toLocaleDateString(this.currentLanguageCode, {
        day: "2-digit"
      });
      return `${yr}-${mo}-${da}`;
    },

    getTimeFromTimestamp(ts) {
      let date = new Date(ts);
      let hr = String(date.getHours()).padStart(2, "0");
      let min = String(date.getMinutes()).padStart(2, "0");
      return `${hr}:${min}`;
    }
  },
  mounted() {
    this.$http
      .get("/api/v1/courses/courses")
      .then(
        resp => (this.availableCourses = resp.data.filter(item => item.active))
      );
  }
};
</script>
