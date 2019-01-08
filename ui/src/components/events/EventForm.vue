<template>
  <v-card>
    <v-card-title>
      <span class="headline">
        {{
        editMode ? "Edit Event" : "Create Event"
        }}
      </span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-toolbar dense floating>
          <v-text-field hide-details prepend-icon="search" single-line></v-text-field>
        </v-toolbar>

        <v-text-field
          v-model="event.title"
          label="Event Title"
          name="title"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('title')"
        ></v-text-field>
        <v-textarea
          rows="3"
          v-model="event.description"
          label="Event Description"
          name="description"
          v-bind:error-messages="errors.collect('description')"
        ></v-textarea>
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
            >
              <v-text-field
                slot="activator"
                v-model="event.startDate"
                label="Start Date"
                prepend-icon="event"
                readonly
              ></v-text-field>

              <v-date-picker
                v-bind:locale="currentLanguageCode"
                v-model="event.startDate"
                @input="showStartDatePicker = false"
              ></v-date-picker>
            </v-menu>
          </v-flex>
          <v-flex xs12 md6 ml-5>
            <!-- Start Time -->
            <v-dialog
              ref="dialog1"
              v-model="startTimeModal"
              :return-value.sync="event.startTime"
              lazy
              full-width
              width="290px"
              persistent
            >
              <v-text-field
                slot="activator"
                v-model="event.startTime"
                label="Start Time"
                prepend-icon="schedule"
                readonly
              ></v-text-field>
              <v-time-picker v-if="startTimeModal" format="24hr" v-model="event.startTime">
                <v-spacer></v-spacer>
                <v-btn flat color="primary" @click="startTimeModal = false">Cancel</v-btn>
                <v-btn flat color="primary" @click="$refs.dialog1.save(event.startTime)">OK</v-btn>
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
            >
              <v-text-field
                slot="activator"
                v-model="event.endDate"
                label="End Date"
                prepend-icon="event"
                readonly
              ></v-text-field>

              <v-date-picker
                v-bind:locale="currentLanguageCode"
                v-model="event.endDate"
                @input="showEndDatePicker = false"
              ></v-date-picker>
            </v-menu>
          </v-flex>
          <v-flex xs12 md6 ml-5>
            <!-- End Time -->
            <v-dialog
              ref="dialog2"
              v-model="endTimeModal"
              :return-value.sync="event.endTime"
              lazy
              full-width
              width="290px"
              persistent
            >
              <v-text-field
                slot="activator"
                v-model="event.endTime"
                label="End Time"
                prepend-icon="update"
                readonly
              ></v-text-field>
              <v-time-picker v-if="endTimeModal" format="24hr" v-model="event.endTime">
                <v-spacer></v-spacer>
                <v-btn flat color="primary" @click="endTimeModal = false">Cancel</v-btn>
                <v-btn flat color="primary" @click="$refs.dialog2.save(event.endTime)">OK</v-btn>
              </v-time-picker>
            </v-dialog>
          </v-flex>
        </v-layout>
      </form>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="primary" flat v-on:click="cancel">{{ $t("actions.cancel") }}</v-btn>
      <v-btn color="primary" flat v-on:click="clear">{{ $t("actions.clear") }}</v-btn>
      <v-btn color="primary" v-on:click="save">
        {{
        $t("actions.save")
        }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { isEmpty } from "lodash";
import { mapGetters } from "vuex";

export default {
  name: "EventForm",
  watch: {
    // Make sure data stays in sync with any changes to `initialData` from parent.
    initialData(eventProp) {
      if (isEmpty(eventProp)) {
        this.clear();
      } else {
        this.event = eventProp;
      }
    }
  },
  computed: {
    // List the keys in an Event record.
    eventKeys() {
      return Object.keys(this.event);
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
      this.$validator.reset();
    },
    save() {
      this.$validator.validateAll();
      if (!this.errors.any()) {
        this.$emit("save", this.event);
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
    }
  },
  data: function() {
    return {
      event: {},
      showStartDatePicker: false,
      showEndDatePicker: false,
      startTimeModal: false,
      endTimeModal: false
    };
  }
};
</script>
