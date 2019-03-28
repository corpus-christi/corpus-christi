<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
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
                :multiple="!editMode"
                chips
                small-chips
                v-bind:label="$t(editMode ? 'courses.date' : 'courses.dates')"
                prepend-icon="event"
                readonly
                data-cy="course-offering-date"
              ></v-combobox>
              <v-date-picker
                v-model="dates"
                :multiple="!editMode"
                no-title
                scrollable
                v-bind:locale="currentLanguageCode"
                data-cy="course-offering-date-picker"
              >
                <v-spacer></v-spacer>
                <v-btn
                  flat
                  color="primary"
                  @click="showDatePicker = false"
                  data-cy="course-offering-date-cancel"
                  >{{ $t("actions.cancel") }}</v-btn
                >
                <v-btn
                  flat
                  color="primary"
                  @click="$refs.dateMenu.save(dates)"
                  data-cy="course-offering-date-ok"
                  >{{ $t("actions.confirm") }}</v-btn
                >
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
                  >{{ $t("actions.cancel") }}</v-btn
                >
                <v-btn
                  flat
                  color="primary"
                  @click="$refs.timeMenu.save(time)"
                  data-cy="course-offering-time-ok"
                  >{{ $t("actions.confirm") }}</v-btn
                >
              </v-time-picker>
            </v-menu>
          </v-flex>
        </v-layout>

        <p class="caption" v-if="!editMode">
          {{ $t("courses.info-meeting-dates") }}
        </p>

        <!-- teacher -->
        <EntitySearch
          person
          v-model="teacher"
          name="teacher"
          v-validate="'required'"
          v-bind:error-messages="errors.first('teacher')"
          :label="$t('courses.teacher')"
          data-cy="course-offering-teacher"
        />

        <!-- location -->
        <EntitySearch
          location
          v-model="location"
          name="location"
          v-validate="'required'"
          v-bind:error-messages="errors.first('location')"
          :label="$t('courses.location')"
          data-cy="course-offering-location"
        />
      </form>
    </v-card-text>
    <v-card-actions>
      <v-btn color="secondary" flat :disabled="saving" v-on:click="cancel">{{
        $t("actions.cancel")
      }}</v-btn>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        raised
        :disabled="saving"
        :loading="saving"
        v-on:click="save"
      >
        {{ $t("actions.save") }}
        <v-progress-circular
          v-if="!editMode"
          slot="loader"
          :size="20"
          :width="3"
          v-model="savingProgress"
        />
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { isEmpty, clone, cloneDeep } from "lodash";
import EntitySearch from "../EntitySearch";
import { mapGetters } from "vuex";

export default {
  name: "ClassMeetingForm",

  components: {
    EntitySearch
  },

  data() {
    return {
      saving: false,
      savingProgress: 0,

      classMeeting: {},
      dates: "",
      time: "",
      teacher: {},
      location: {},

      showDatePicker: false,
      showTimePicker: false
    };
  },

  computed: {
    title() {
      return this.editMode
        ? this.$t("actions.edit")
        : this.$t("courses.new-meeting");
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
    initialData(prop) {
      if (isEmpty(prop)) {
        this.clear();
      } else {
        this.classMeeting = prop;
        if (this.editMode) {
          this.dates = this.getDateFromTimestamp(this.classMeeting.when);
          this.time = this.getTimeFromTimestamp(this.classMeeting.when);
          this.teacher = this.classMeeting.teacher;
          this.location = this.classMeeting.location;
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
    offeringId: {
      type: [String, Number],
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
      this.dates = this.editMode ? "" : [];
      this.time = "";
      this.teacher = {};
      this.location = {};
      this.$validator.reset();
    },

    save() {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          this.saving = true;
          let classMeeting = cloneDeep(this.classMeeting);
          this.saveClassMeeting(classMeeting);
        }
      });
    },

    saveClassMeeting() {
      if (this.editMode) {
        let meeting = {};
        meeting.offeringId = this.offeringId;
        meeting.locationId = this.location.id;
        meeting.teacherId = this.teacher.id;
        meeting.when = this.getTimestamp(this.dates, this.time);

        this.$http
          .patch(
            `/api/v1/courses/course_offerings/${this.offeringId}/${
              this.classMeeting.id
            }`,
            meeting
          )
          .then(resp => {
            let newMeeting = resp.data;
            newMeeting.location = this.location;
            newMeeting.teacher = this.teacher;
            this.$emit("save", [newMeeting]); // Parent expects array of updated records
          })
          .catch(err => {
            this.$emit("save", err);
          })
          .finally(() => {
            this.saving = false;
          });
      } else {
        let meetingTemplate = {};
        meetingTemplate.offeringId = this.offeringId;
        meetingTemplate.locationId = this.location.id;
        meetingTemplate.teacherId = this.teacher.id;

        let meetings = [];

        this.dates.forEach(date => {
          let meeting = clone(meetingTemplate);
          meeting.when = this.getTimestamp(date, this.time);
          meetings.push(meeting);
        });

        let savingCount = 0;
        this.savingProgress = 0;

        let promises = meetings.map(meeting => {
          return this.$http
            .post(
              `/api/v1/courses/course_offerings/${
                this.offeringId
              }/class_meetings`,
              meeting
            )
            .then(resp => {
              savingCount += 1;
              this.savingProgress = (100 * savingCount) / promises.length;

              // Build a full object to return to parent
              let newMeeting = resp.data;
              newMeeting.location = this.location;
              newMeeting.teacher = this.teacher;
              return newMeeting;
            });
        });

        Promise.all(promises)
          .then(newMeetings => {
            this.$emit("save", newMeetings);
          })
          .catch(err => {
            this.$emit("save", err);
          })
          .finally(() => {
            this.saving = false;
          });
      }
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
  }
};
</script>

<style></style>
