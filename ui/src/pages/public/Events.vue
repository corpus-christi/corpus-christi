<template>
  <v-container grid-list-md>
    <v-layout row wrap>
      <v-flex xs12 sm12 md4>
        <h1 style="margin-left: 25px;">
          {{ $t("public.headers.upcoming-events") }}
        </h1>
      </v-flex>
      <v-spacer></v-spacer>

      <!-- Start Date -->
      <v-flex xs12 sm4 md3>
        <v-menu
          :close-on-content-click="false"
          v-model="showStartDatePicker"
          :nudge-right="40"
          lazy
          transition="scale-transition"
          offset-y
          full-width
          min-width="290px"
          data-cy="start-date-picker"
        >
          <v-text-field
            slot="activator"
            v-model="filterStart"
            v-bind:label="$t('events.start-date')"
            prepend-icon="event"
            readonly
          ></v-text-field>
          <v-date-picker
            v-model="filterStart"
            @input="showStartDatePicker = false"
            v-bind:locale="currentLanguageCode"
          ></v-date-picker>
        </v-menu>
      </v-flex>

      <!-- End Date -->
      <v-flex xs12 sm4 md3>
        <v-menu
          :close-on-content-click="false"
          v-model="showEndDatePicker"
          :nudge-right="40"
          lazy
          transition="scale-transition"
          offset-y
          full-width
          min-width="290px"
          data-cy="end-date-picker"
        >
          <v-text-field
            slot="activator"
            v-model="filterEnd"
            v-bind:label="$t('events.end-date')"
            prepend-icon="event"
            readonly
          ></v-text-field>
          <v-date-picker
            v-model="filterEnd"
            @input="showEndDatePicker = false"
            v-bind:locale="currentLanguageCode"
            :min="filterStart"
          ></v-date-picker>
        </v-menu>
      </v-flex>
    </v-layout>

    <!-- Cards -->
    <v-layout layout row wrap>
      <v-flex
        xs12
        sm6
        md4
        lg4
        v-for="event in filteredEvents"
        v-bind:key="event.id"
      >
        <EventCard :event="event"></EventCard>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import EventCard from "../../components/public/EventCard";
import { mapGetters } from "vuex";

export default {
  name: "Events",
  components: {
    EventCard
  },
  data() {
    return {
      events: [],
      pageLoaded: false,
      filterStart: "",
      filterEnd: "",
      showStartDatePicker: false,
      showEndDatePicker: false
    };
  },
  mounted() {
    this.pageLoaded = false;
    this.$http
      .get(`/api/v1/events/?return_group=all&include_images=1&sort=start`)
      .then(resp => {
        this.events = resp.data;
        this.pageLoaded = true;
      });

    this.filterStart = this.today;
    this.filterEnd = this.addDaystoDate(this.today, 30);
  },

  computed: {
    today() {
      return this.getDateFromTimestamp(Date.now());
    },

    filteredEvents() {
      const start = this.getTimestamp(this.filterStart);
      const end = this.getTimestamp(this.addDaystoDate(this.filterEnd, 1));

      return this.events.filter(
        ev => new Date(ev.start) <= end && new Date(ev.start) >= start
      );
    },

    ...mapGetters(["currentLanguageCode"])
  },

  methods: {
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

    getTimestamp(date) {
      let datems = new Date(date).getTime();
      let tzoffset = new Date().getTimezoneOffset() * 60000;
      return new Date(datems + tzoffset);
    },

    addDaystoDate(date, dayDuration) {
      let date1 = this.getTimestamp(date);
      date1.setDate(date1.getDate() + dayDuration);
      return this.getDateFromTimestamp(date1);
    }
  }
};
</script>

<style scoped></style>
