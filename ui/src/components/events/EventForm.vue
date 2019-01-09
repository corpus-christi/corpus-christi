<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-text-field
          v-model="event.title"
          v-bind:label="$t('events.title')"
          name="title"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('title')"
          data-cy="title"
        ></v-text-field>
        <v-textarea
          rows="3"
          v-model="event.description"
          v-bind:label="$t('events.event-description')"
          name="description"
          v-bind:error-messages="errors.collect('description')"
          data-cy="description"
        ></v-textarea>

        <event-location v-on:setLocation="setLocation" />

        <v-layout>
          <v-flex xs12 md6>
            <!-- Start Date -->
            <v-menu
              :close-on-content-click="false"
              v-model="showStartDatePicker"
              :nudge-right="40"
              lazy
              transition="scale-transition"
              offset-y
              full-width
              min-width="290px"
              data-cy="start-date-menu"
            >
              <v-text-field
                slot="activator"
                v-model="startDate"
                v-bind:label="$t('events.start-date')"
                prepend-icon="event"
                readonly
              ></v-text-field>

              <v-date-picker
                v-bind:locale="currentLanguageCode"
                v-model="startDate"
                @input="showStartDatePicker = false"
                data-cy="start-date-picker"
              ></v-date-picker>
            </v-menu>
          </v-flex>
          <v-flex xs12 md6 ml-5>
            <!-- Start Time -->
            <v-dialog
              ref="dialog1"
              v-model="startTimeModal"
              :return-value.sync="startTime"
              lazy
              full-width
              width="290px"
              persistent
              data-cy="start-time-dialog"
            >
              <v-text-field
                slot="activator"
                v-model="startTime"
                v-bind:label="$t('events.start-time')"
                prepend-icon="schedule"
                readonly
              ></v-text-field>
              <v-time-picker
                v-if="startTimeModal"
                :format="timeFormat"
                v-model="startTime"
                data-cy="start-time-picker"
              >
                <v-spacer></v-spacer>
                <v-btn
                  flat color="primary"
                  @click="startTimeModal = false"
                  data-cy="start-time-cancel"
                  >{{ $t('actions.cancel') }}</v-btn
                >
                <v-btn
                  flat
                  color="primary"
                  @click="$refs.dialog1.save(startTime)"
                  data-cy="start-time-ok"
                  >{{ $t('actions.confirm') }}</v-btn
                >
              </v-time-picker>
            </v-dialog>
          </v-flex>
        </v-layout>
        <v-layout>
          <v-flex xs12 md6>
            <!-- End Date -->
            <v-menu
              :close-on-content-click="false"
              v-model="showEndDatePicker"
              :nudge-right="40"
              lazy
              transition="scale-transition"
              offset-y
              full-width
              min-width="290px"
              data-cy="end-date-menu"
            >
              <v-text-field
                slot="activator"
                v-model="endDate"
                v-bind:label="$t('events.end-date')"
                prepend-icon="event"
                readonly
              ></v-text-field>

              <v-date-picker
                v-bind:locale="currentLanguageCode"
                v-model="endDate"
                @input="showEndDatePicker = false"
                data-cy="end-date-picker"
              ></v-date-picker>
            </v-menu>
          </v-flex>
          <v-flex xs12 md6 ml-5>
            <!-- End Time -->
            <v-dialog
              ref="dialog2"
              v-model="endTimeModal"
              :return-value.sync="endTime"
              lazy
              full-width
              width="290px"
              persistent
              data-cy="end-time-dialog"
            >
              <v-text-field
                slot="activator"
                v-model="endTime"
                v-bind:label="$t('events.end-time')"
                prepend-icon="update"
                readonly
              ></v-text-field>
              <v-time-picker
                v-if="endTimeModal"
                :format="timeFormat"
                v-model="endTime"
                data-cy="end-time-picker"
              >
                <v-spacer></v-spacer>
                <v-btn
                  flat
                  color="primary"
                  @click="endTimeModal = false"
                  data-cy="end-time-cancel"
                  >{{ $t('actions.cancel') }}</v-btn
                >
                <v-btn
                  flat
                  color="primary"
                  @click="$refs.dialog2.save(endTime)"
                  data-cy="end-time-ok"
                  >{{ $t('actions.confirm') }}</v-btn
                >
              </v-time-picker>
            </v-dialog>
          </v-flex>
        </v-layout>
      </form>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        flat
        v-on:click="cancel"
        data-cy="form-cancel"
        >{{ $t("actions.cancel") }}</v-btn
      >
      <v-btn
        color="primary"
        flat
        v-on:click="clear"
        data-cy="form-clear"
      >{{ $t("actions.clear") }}</v-btn>
      <v-btn color="primary"
        v-on:click="save"
        data-cy="form-save"
      >{{ $t("actions.save") }}</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { isEmpty } from "lodash";
import { mapGetters } from "vuex";
import EventLocation from "./EventLocation";
export default {
  components: { "event-location": EventLocation },
  name: "EventForm",
  watch: {
    // Make sure data stays in sync with any changes to `initialData` from parent.
    initialData(eventProp) {
      if (isEmpty(eventProp)) {
        this.clear();
      } else {
        this.event = eventProp;
        if (this.event.start && this.event.start.length > 0) {
          this.event.start = new Date(this.event.start);
          this.startTime = this.getTimeFromTimestamp(this.event.start);
          this.startDate = this.getDateFromTimestamp(this.event.start);
        }
        if (this.event.end && this.event.end.length > 0) {
          this.event.end = new Date(this.event.end);
          this.endTime = this.getTimeFromTimestamp(this.event.end);
          this.endDate = this.getDateFromTimestamp(this.event.end);
        }
      }
    }
  },
  computed: {
    // List the keys in an Event record.
    eventKeys() {
      return Object.keys(this.event);
    },
    title() {
      return this.editMode
        ? this.$t("events.edit-event")
        : this.$t("events.create-event");
    },

    timeFormat() {
      if (this.currentLanguageCode == "en") {
        return "ampm";
      } else return "24hr";
    },

    ...mapGetters(["currentLanguageCode"])
  },

  methods: {
    cancel() {
      this.clear();
      this.$emit("cancel");
    },

    // Clear the form and the validators.
    clear() {
      for (let key of this.eventKeys) {
        this.event[key] = "";
      }
      this.startTime = "";
      this.startDate = "";
      this.endTime = "";
      this.endDate = "";
      this.showStartDatePicker = false;
      this.showEndDatePicker = false;
      this.startTimeModal = false;
      this.endTimeModal = false;

      this.$validator.reset();
    },
    save() {
      this.$validator.validateAll();
      if (!this.errors.any()) {
        this.event.start = this.getTimestamp(this.startDate, this.startTime);
        this.event.end = this.getTimestamp(this.endDate, this.endTime);

        this.$emit("save", this.event);
      }
    },

    getTimestamp(date, time) {
      let datems = new Date(date).getTime();
      let timearr = time.split(":");
      let timemin = Number(timearr[0]) * 60 + Number(timearr[1]);
      let timems = timemin * 60000;
      return new Date(datems + timems);
    },

    getDateFromTimestamp(ts) {
      let date = new Date(ts);
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
    },

    setLocation(locationId) {
      console.log("Setting Location");
      console.log(locationId);
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
    }
  },
  data: function() {
    return {
      event: {},
      startTime: "",
      startDate: "",
      endTime: "",
      endDate: "",
      showStartDatePicker: false,
      showEndDatePicker: false,
      startTimeModal: false,
      endTimeModal: false
    };
  }
};
</script>
