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
          <v-card-text class="pa-4">
            <div>
              <b>Location: </b>
              <div class="multi-line ml-2">{{ displayLocation }}</div>
            </div>
            <div><b>Start: </b>{{ getDisplayDate(event.start) }}</div>
            <div><b>End: </b>{{ getDisplayDate(event.end) }}</div>
            <div class="mt-2">{{ event.description }}</div>
          </v-card-text>
          <v-card-actions>
            <v-btn
              flat
              ripple
              color="primary"
              v-on:click="navigateTo('/participants')"
            >
              <v-icon>person</v-icon>&nbsp;{{ $t("events.participants.title") }}
            </v-btn>
            <v-btn
              flat
              ripple
              color="primary"
              v-on:click="navigateTo('/teams')"
            >
              <v-icon>group</v-icon>&nbsp;{{ $t("events.teams.title") }}
            </v-btn>
            <v-btn
              flat
              ripple
              color="primary"
              v-on:click="navigateTo('/assets')"
            >
              <v-icon>devices_other</v-icon>&nbsp;{{ $t("assets.title") }}
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
    this.$http.get(`/api/v1/events/${id}`).then(resp => {
      this.event = resp.data;
      console.log(resp.data);
      this.pageLoaded = true;
    });
  },

  computed: {
    displayLocation() {
      let location = this.event.location;
      let str = "";
      if (location) {
        str += `${location.description}`;
        if (location.address) {
          str += `\n${location.address.name}`;
          str += `\n${location.address.address}`;
          str += `\n${location.address.city}, ${location.address.country.code}`;
        }
      }
      return str;
    },

    ...mapGetters(["currentLanguageCode"])
  },

  data() {
    return {
      event: {},
      eventDialog: {
        show: false,
        saveLoading: false,
        event: {}
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
      const id = this.event.id;
      delete event.id;
      event.location_id = event.location.id;
      delete event.location;
      this.$http
        .put(`/api/v1/events/${id}`, event)
        .then(resp => {
          console.log("EDITED", resp);
          this.event = resp.data;
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

    navigateTo(path) {
      this.$router.push({
        path: "/events/" + this.$route.params.event + path
      });
    },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    }
  }
};
</script>

<style scoped>
.multi-line {
  white-space: pre;
}
</style>
