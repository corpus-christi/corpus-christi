<template>
  <div>
    <vue-cal
      :locale="currentLocale.code.split('-')[0]"
      default-view="week"
      events-on-month-view
      :events="calendarEvents"
    >
    </vue-cal>
    <v-dialog v-model="dialog.show" width="500">
      <v-card>
        <v-card-title class="headline" primary-title>
          {{ dialog.event ? dialog.event.title : "" }}
        </v-card-title>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" flat v-on:click="goToEvent">
            Go to Event
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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
      originalEvents: [],
      events: [],
      dialog: {
        show: false,
        event: null
      }
    };
  },
  mounted() {
    this.tableLoading = true;
    this.$http.get("/api/v1/events/?return_group=all").then(resp => {
      this.originalEvents = resp.data;
      var currentDate = new Date();
      for (let event in resp.data) {
        this.events.push({
          event: resp.data[event],
          start: this.getDate(resp.data[event].start),
          end: this.getDate(resp.data[event].end),
          description: resp.data[event].description,
          class:
            new Date(resp.data[event].end) < currentDate ? "leisure" : "sport",
          content:
            `<a href="/event/${resp.data[event].id}">${resp.data[event].title}</a>`
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
    logEvents(text, event) {
      console.log(text, event);
      this.dialog.show = true;
      this.dialog.event = event.event;
    },
    goToEvent() {
      this.dialog.show = false;
      let routeData = this.$router.resolve({
        path: "/event/" + this.dialog.event.id
      });
      window.open(routeData.href, "_blank");
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
