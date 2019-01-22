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
    this.$http.get("/api/v1/events/?return_group=all").then(resp => {
      var currentDate = new Date();
      for (let event of resp.data) {
        this.events.push({
          event: event,
          start: this.getDate(event.start),
          end: this.getDate(event.end),
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
    getDate(obj) {
      var d = new Date(obj);
      return obj.slice(0, 10) + " " + d.getUTCHours() + ":" + d.getUTCMinutes();
    },

    getTemplate(event) {
      return `<span data-cy="cal-event-${event.id}">${event.title}</span>`;
    },

    goToEvent(e) {
      this.$router.push({ path: "/event/" + e.event.id + "/details" });
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
