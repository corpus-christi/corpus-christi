<template>
  <v-layout column>
    <v-flex xs12>
      <v-card class="ma-1">
        <template v-if="eventLoaded">
          <v-container fill-height fluid>
            <v-flex xs9 sm9 align-end flexbox>
              <span class="headline">{{ event.title }}</span>
            </v-flex>
            <v-layout xs3 sm3 align-end justify-end>
              <v-btn
                flat
                color="primary"
                data-cy="edit-event"
                v-on:click="editEvent(event)"
              >
                <v-icon>edit</v-icon>&nbsp;{{ $t("actions.edit") }}
              </v-btn>
            </v-layout>
          </v-container>
          <v-card-text class="pa-4">
            <div v-if="event.location">
              <b>{{ $t("events.location") }}: </b>
              <div class="multi-line ml-2">{{ displayLocation }}</div>
            </div>
            <div>
              <b>{{ $t("events.start-time") }}: </b
              >{{ getDisplayDate(event.start) }}
            </div>
            <div>
              <b>{{ $t("events.end-time") }}: </b
              >{{ getDisplayDate(event.end) }}
            </div>
            <div class="mt-2">{{ event.description }}</div>
          </v-card-text>
          <v-card-actions>
            <v-btn
              flat
              ripple
              color="primary"
              data-cy="navigate-to-participants"
              v-on:click="navigateTo('/participants')"
            >
              <v-icon>person</v-icon>&nbsp;{{ $t("events.participants.title") }}
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
    <v-layout column wrap>
      <v-flex xs12>
        <event-team-details
          :teams="event.teams"
          :loaded="teamsLoaded"
          v-on:snackbar="showSnackbar($event)"
          v-on:team-added="getEvent()"
        ></event-team-details>
      </v-flex>
      <v-flex xs12>
        <event-person-details
          :persons="event.persons"
          :loaded="personsLoaded"
          v-on:snackbar="showSnackbar($event)"
          v-on:person-added="getEvent()"
        ></event-person-details>
      </v-flex>
      <v-flex xs12>
        <event-asset-details
          :assets="event.assets"
          :loaded="assetsLoaded"
          v-on:snackbar="showSnackbar($event)"
          v-on:asset-added="getEvent()"
        ></event-asset-details>
      </v-flex>
    </v-layout>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false" data-cy="close-snackbar">
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>

    <!-- Edit Event dialog -->
    <v-dialog v-model="eventDialog.show" persistent max-width="500px">
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
import EventTeamDetails from "./EventTeamDetails";
import EventAssetDetails from "./EventAssetDetails";
import EventPersonDetails from "./EventPersonDetails";

export default {
  name: "EventDetails",
  components: {
    "event-form": EventForm,
    "event-team-details": EventTeamDetails,
    "event-asset-details": EventAssetDetails,
    "event-person-details": EventPersonDetails
  },

  data() {
    return {
      event: {},
      eventDialog: {
        show: false,
        saveLoading: false,
        event: {}
      },

      addAssetDialog: {
        show: false,
        loading: false,
        asset: null
      },

      deleteAssetDialog: {
        show: false,
        loading: false,
        assetId: -1
      },

      snackbar: {
        show: false,
        text: ""
      },
      eventLoaded: false,
      teamsLoaded: false,
      assetsLoaded: false,
      personsLoaded: false
    };
  },

  mounted() {
    this.eventLoaded = false;
    this.teamsLoaded = false;
    this.assetsLoaded = false;
    this.personsLoaded = false;
    this.getEvent().then(() => {
      this.eventLoaded = true;
      this.teamsLoaded = true;
      this.assetsLoaded = true;
      this.personsLoaded = true;
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

  methods: {
    getEvent() {
      const id = this.$route.params.event;
      return this.$http
        .get(
          `/api/v1/events/${id}?include_teams=1&include_assets=1&include_persons=1`
        )
        .then(resp => {
          this.event = resp.data;
          this.event.teams = !this.event.teams
            ? []
            : this.event.teams.map(t => t.team);
          this.event.assets = !this.event.assets
            ? []
            : this.event.assets.map(a => a.asset);
          // conserve description on EventPersons
          this.event.persons = !this.event.persons
            ? []
            : this.event.persons.map(p =>
                Object.assign(p, { id: p.person_id })
              );
        });
    },

    reloadTeams() {
      this.teamsLoaded = false;
      const id = this.$route.params.event;
      this.$http.get(`/api/v1/events/${id}?include_teams=1`).then(resp => {
        let eventData = resp.data;
        this.event.teams = !eventData.teams
          ? []
          : eventData.teams.map(t => t.team);
        this.teamsLoaded = true;
      });
    },

    reloadAssets() {
      this.assetsLoaded = false;
      const id = this.$route.params.event;
      this.$http.get(`/api/v1/events/${id}?include_assets=1`).then(resp => {
        let eventData = resp.data;
        this.event.assets = !eventData.assets
          ? []
          : eventData.assets.map(a => a.asset);
        this.assetsLoaded = true;
      });
    },

    reloadPersons() {
      this.personsLoaded = false;
      const id = this.$route.params.event;
      this.$http.get(`/api/v1/events/${id}?include_persons=1`).then(resp => {
        let eventData = resp.data;
        this.event.persons = !eventData.persons
          ? []
          : eventData.persons.map(p => Object.assign(p, { id: p.person_id }));
        this.personsLoaded = true;
      });
    },

    editEvent(event) {
      this.eventDialog.event = JSON.parse(JSON.stringify(event));
      this.eventDialog.show = true;
    },

    cancelEvent() {
      this.eventDialog.show = false;
    },

    saveEvent(event) {
      this.eventDialog.saveLoading = true;
      if (event.location) {
        event.location_id = event.location.id;
      }
      let newEvent = JSON.parse(JSON.stringify(event));
      delete newEvent.location;
      delete newEvent.assets;
      delete newEvent.teams;
      delete newEvent.persons;
      delete newEvent.dayDuration;
      delete newEvent.teams;
      delete newEvent.id;
      const eventId = event.id;
      this.$http
        .put(`/api/v1/events/${eventId}`, newEvent)
        .then(resp => {
          console.log("EDITED", resp);
          this.eventDialog.show = false;
          this.eventDialog.saveLoading = false;
          this.eventLoaded = false;
          this.getEvent().then(() => (this.eventLoaded = true));
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
