<template>
  <v-layout>
    <v-flex xs12 sm12>
      <v-card>
        <template v-if="pageLoaded">
          <v-container fill-height fluid>
            <v-flex xs9 sm9 align-end flexbox>
              <span class="headline">{{ event.title }}</span>
            </v-flex>
            <v-layout xs3 sm3 align-end justify-end>
              <v-btn flat color="primary" v-on:click="editEvent(event)">
                <v-icon>edit</v-icon>&nbsp;{{ $t("actions.edit") }}
              </v-btn>
            </v-layout>
          </v-container>
          <v-card-text>
            <div><b>Location: </b>{{ event.location_name }}</div>
            <div><b>Start: </b>{{ getDisplayDate(event.start) }}</div>
            <div><b>End: </b>{{ getDisplayDate(event.end) }}</div>
            <div>{{ event.description }}</div>
          </v-card-text>
          <v-card-actions>
            <v-btn
              flat
              color="primary"
              v-on:click="
                $router.push({
                  path: '/events/' + $route.params.event + '/participants'
                })
              "
            >
              <v-icon>person</v-icon>&nbsp;{{ $t("events.participants.title") }}
            </v-btn>
            <v-btn
              flat
              color="primary"
              v-on:click="
                $router.push({
                  path: '/events/' + $route.params.event + '/teams'
                })
              "
            >
              <v-icon>group</v-icon>&nbsp;{{ $t("events.teams.title") }}
            </v-btn>
            <v-btn
              flat
              color="primary"
              v-on:click="
                $router.push({
                  path: '/events/' + $route.params.event + '/assets'
                })
              "
            >
              <v-icon>devices_other</v-icon>&nbsp;{{
                $t("events.assets.title")
              }}
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
    <v-dialog v-model="eventDialog.show" max-width="500px">
      <event-form
        v-bind:editMode="true"
        v-bind:initialData="eventDialog.event"
        v-bind:saveLoading="eventDialog.saveLoading"
        v-bind:addMoreLoading="eventDialog.addMoreLoading"
        v-on:cancel="cancelEvent"
        v-on:save="saveEvent"
      />
    </v-dialog>
  </v-layout>
</template>

<script>
import EventForm from "./EventForm";
import { mapGetters } from "vuex";

export default {
  name: "EventDetails",
  components: { "event-form": EventForm },

  mounted() {
    this.pageLoaded = false;
    const id = this.$route.params.event;
    this.$http.get(`http://localhost:3000/events/${id}`).then(resp => {
      this.event = resp.data;
      this.pageLoaded = true;
    });
  },

  computed: {
    ...mapGetters(["currentLanguageCode"])
  },

  data() {
    return {
      event: {},
      eventDialog: {
        event: {},
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
  methods: {
    editEvent(event) {
      this.eventDialog.event = JSON.parse(JSON.stringify(event));
      this.eventDialog.show = true;
    },

    cancelEvent() {
      this.eventDialog.show = false;
    },

    saveEvent(event) {
      this.eventDialog.saveLoading = true;
      const eventId = event.id;
      const idx = this.events.findIndex(ev => ev.id === event.id);
      delete event.id;
      this.$http
        .put(`http://localhost:3000/events/${eventId}`, event)
        .then(resp => {
          console.log("EDITED", resp);
          Object.assign(this.events[idx], event);
          this.eventDialog.show = false;
          this.eventDialog.saveLoading = false;
          this.showSnackbar(this.$t("events.event-edited"));
        })
        .catch(err => {
          console.error("PUT FALURE", err.response);
          this.eventDialog.saveLoading = false;
          this.showSnackbar(this.$t("events.error-editing-event"));
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

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    }
  }
};
</script>
