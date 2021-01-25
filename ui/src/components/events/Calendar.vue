<template>
  <div>
    <v-card>
      <v-card-title>{{ $t("events.calendar.title") }}</v-card-title>
      <v-tabs centered fixed-tabs color="#e69635" v-model="type">
        <v-tab @click="type = 0">{{ $t("events.calendar.month") }}</v-tab>
        <v-tab @click="type = 1">{{ $t("events.calendar.week") }}</v-tab>
        <v-tab @click="type = 2">{{ $t("events.calendar.day") }}</v-tab>
      </v-tabs>

      <v-container>
        <v-row>
          <v-spacer />
          <v-btn fab left icon @click="prev">
            <v-icon>chevron_left</v-icon>
          </v-btn>

          <v-card-subtitle>{{
            getDateString(this.types[this.type])
          }}</v-card-subtitle>

          <v-btn fab right icon @click="next">
            <v-icon>chevron_right</v-icon>
          </v-btn>
          <v-spacer />
        </v-row>
      </v-container>

      <v-calendar
        ref="calendar"
        :locale="currentLocaleModel.languageCode"
        :type="types[type]"
        :events="calendarEvents"
        v-model="calendarDate"
        @click:event="goToEvent"
        @click:date="type = 2"
        event-color="orange"
        color="#e69635"
      >
      </v-calendar>
    </v-card>
  </div>
</template>
<script>
import { mapGetters, mapState } from "vuex";
export default {
  components: {},
  data() {
    return {
      calendarDate: "",
      events: [],
      type: 0,
      types: ["month", "week", "day"],
    };
  },
  mounted() {
    this.tableLoading = true;
    this.$http.get("/api/v1/events/").then((resp) => {
      var currentDate = new Date();
      this.calendarDate = currentDate;
      this.selectedDate = currentDate;
      for (let event of resp.data) {
        this.events.push({
          event: event,
          id: event.id,
          name: event.title, // Attribute is named "name" to correspond with Vuetify's v-calendar :events input syntax
          start: this.getDatetime(event.start),
          end: this.getDatetime(event.end),
          description: event.description,
          class: new Date(event.end) < currentDate ? "leisure" : "sport",
          content: this.getTemplate(event),
        });
      }
    });
  },

  computed: {
    calendarEvents() {
      return this.events;
    },
    ...mapState(["locales"]),
    ...mapGetters(["currentLocaleModel"]),
  },

  methods: {
    getDatetime(ts) {
      let date = this.getDateFromTimestamp(ts);
      let time = this.getTimeFromTimestamp(ts);
      return `${date} ${time}`;
    },

    getTemplate(event) {
      return `<span data-cy="cal-event-${event.id}">${event.title}</span>`;
    },

    goToEvent(e) {
      this.$router.push({ path: "/event/" + e.event.id + "/details" });
    },

    getDateFromTimestamp(ts) {
      let date = new Date(ts);
      if (date.getTime() < 86400000) {
        //ms in a day
        return "";
      }
      let yr = date.toLocaleDateString(this.currentLanguageCode, {
        year: "numeric",
      });
      let mo = date.toLocaleDateString(this.currentLanguageCode, {
        month: "2-digit",
      });
      let da = date.toLocaleDateString(this.currentLanguageCode, {
        day: "2-digit",
      });
      return `${yr}-${mo}-${da}`;
    },

    getTimeFromTimestamp(ts) {
      let date = new Date(ts);
      let hr = String(date.getHours()).padStart(2, "0");
      let min = String(date.getMinutes()).padStart(2, "0");
      return `${hr}:${min}`;
    },

    getDateString(type) {
      let dStr = "";
      let tempDate = this.parseDate(this.calendarDate);
      switch (type) {
        case "day":
          dStr = `${tempDate.toLocaleString(
            this.currentLocaleModel.languageCode,
            { dateStyle: "full" }
          )}`;
          break;
        case "week":
          dStr = `${this.$t(
            "events.calendar.week-label"
          )} ${tempDate.toLocaleString(this.currentLocaleModel.languageCode, {
            dateStyle: "long",
          })}`;
          break;
        case "month":
          dStr = `${tempDate.toLocaleString(
            this.currentLocaleModel.languageCode,
            { month: "long", year: "numeric" }
          )}`;
      }
      return dStr;
    },

    parseDate(dateInput) {
      let tempDate = null;
      if (typeof dateInput === typeof "a") {
        let parts = dateInput.split("-");
        tempDate = new Date(parts[0], parts[1] - 1, parts[2]);
      } else {
        tempDate = dateInput;
      }
      return tempDate;
    },

    prev() {
      this.$refs.calendar.prev();
    },

    next() {
      this.$refs.calendar.next();
    },
  },
};
</script>
