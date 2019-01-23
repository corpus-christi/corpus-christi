<template>
  <div>
    <vue-cal
      :locale="currentLocale.code.split('-')[0]"
      default-view="week"
      events-on-month-view
      :events="calendarEvents"
      v-on:event-focus="goToEvent"
    >
    </vue-cal>
  </div>
</template>
<script>
import Vuecal from "vue-cal";
import "vue-cal/dist/vuecal.css";
import { mapGetters, mapState } from "vuex";
export default {
  components: { "vue-cal": Vuecal },
  data() {
    return {
      events: []
    };
  },
  mounted() {
    this.tableLoading = true;
    this.$http.get("/api/v1/events/").then(resp => {
      var currentDate = new Date();
      for (let event of resp.data) {
        this.events.push({
          event: event,
          start: this.getDatetime(event.start),
          end: this.getDatetime(event.end),
          description: event.description,
          class: new Date(event.end) < currentDate ? "leisure" : "sport",
          content: this.getTemplate(event)
        });
      }
    });
  },

  computed: {
    calendarEvents() {
      return this.events;
    },
    ...mapState(["locales"]),
    ...mapGetters(["currentLocale"])
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

<style>
.vuecal__event.sport {
  background-color: rgba(253, 150, 53, 0.9);
  border: 1px solid rgb(230, 150, 53);
  color: #fff;
}
.vuecal__event.leisure {
  background-color: rgba(158, 158, 158, 0.8);
  border: 1px solid rgb(158, 158, 158);
  color: #fff;
}

.vuecal__menu,
.vuecal__cell-events-count {
  background-color: #e69635;
}
.vuecal__menu li {
  border-bottom-color: #fff;
  color: #fff;
}
.vuecal__menu li.active {
  background-color: rgba(255, 255, 255, 0.15);
}
.vuecal__title {
  background-color: rgba(230, 150, 53, 0.5);
}
.vuecal__cell.today,
.vuecal__cell.current {
  background-color: rgba(240, 240, 255, 0.4);
}
.vuecal:not(.vuecal--day-view) .vuecal__cell.selected {
  background-color: rgba(230, 150, 53, 0.1);
}
.vuecal__cell.selected:before {
  border-color: rgba(230, 150, 53, 0.5);
}
</style>
