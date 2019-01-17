<template>
  <v-layout>
    <v-flex xs6 sm6>
      <v-card class="ma-1">
        <template v-if="pageLoaded">
          <v-container fill-height fluid>
            <v-flex xs9 sm9 align-end flexbox>
              <span class="headline">{{ event.title }}</span>
            </v-flex>
            <v-layout xs3 sm3 align-end justify-end>
              <v-btn flat color="primary" data-cy="edit-event" v-on:click="editEvent(event)">
                <v-icon>edit</v-icon>&nbsp;{{ $t("actions.edit") }}
              </v-btn>
            </v-layout>
          </v-container>
          <v-card-text class="pa-4">
            <div v-if="event.location">
              <b>{{ $t("events.location") }}: </b>
              <div class="multi-line ml-2">{{ displayLocation }}</div>
            </div>
            <div><b>{{ $t("events.start-time") }}: </b>{{ getDisplayDate(event.start) }}</div>
            <div><b>{{ $t("events.end-time") }}: </b>{{ getDisplayDate(event.end) }}</div>
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
            <v-btn
              flat
              ripple
              color="primary"
              data-cy="navigate-to-assets"
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
    <v-flex xs6 sm6>
      <v-card class="ma-1">
        <template v-if="pageLoaded">
          <v-container fill-height fluid>
            <v-flex xs9 sm9 align-end flexbox>
              <span class="headline">{{ $t("events.teams.title") }}</span>
            </v-flex>
            <v-layout xs3 sm3 align-end justify-end>
              <v-btn
                flat
                color="primary"
                data-cy="add-team-dialog"
                v-on:click="addTeamDialog.show = true"
              >
                <v-icon>add</v-icon>&nbsp;{{ $t("events.teams.new") }}
              </v-btn>
            </v-layout>
          </v-container>
          <v-list>
            <template v-for="eventTeam in event.teams">
              <v-divider v-bind:key="'divider' + eventTeam.team_id"></v-divider>
              <v-list-tile v-bind:key="eventTeam.team_id">
                <v-list-tile-content>
                  <span>{{ eventTeam.team.description }}</span>
                </v-list-tile-content>
                <v-list-tile-action>
                  <v-btn flat color="primary">
                    <v-icon 
                      v-on:click="showDeleteTeamDialog(eventTeam.team_id)"
                      :data-cy="'deleteTeam-'+eventTeam.team_id"
                      >delete</v-icon
                    >
                  </v-btn>
                </v-list-tile-action>
              </v-list-tile>
            </template>
          </v-list>
        </template>
      </v-card>
    </v-flex>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false" data-cy="close-snackbar">
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>

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

    <!-- Add Team dialog -->
    <v-dialog v-model="addTeamDialog.show" max-width="500px">
      <v-card>
        <v-card-title primary-title>
          <span class="headline">{{ $t("events.teams.new") }}</span>
        </v-card-title>
        <v-card-text>
          <entity-search v-model="addTeamDialog.team" team></entity-search>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelAddTeam()"
            color="secondary"
            flat
            :disabled="addTeamDialog.loading"
            data-cy="cancel-add"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="addTeam()"
            color="primary"
            raised
            :disabled="!addTeamDialog.team"
            :loading="addTeamDialog.loading"
            data-cy="confirm-add"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Team dialog -->
    <v-dialog v-model="deleteTeamDialog.show" max-width="350px">
      <v-card>
        <v-card-text>
          <span>{{ $t("events.teams.confirm-remove-from-event") }}</span>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="deleteTeamDialog.show = false"
            color="secondary"
            flat
            :disabled="deleteTeamDialog.loading"
            data-cy="cancel-delete"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deleteTeam()"
            color="primary"
            raised
            :loading="deleteTeamDialog.loading"
            data-cy="confirm-delete"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-layout>
</template>

<script>
import EventForm from "./EventForm";
import { mapGetters } from "vuex";
import EntitySearch from "../EntitySearch";

export default {
  name: "EventDetails",
  components: {
    "event-form": EventForm,
    "entity-search": EntitySearch
  },

  data() {
    return {
      event: {},
      teams: [],
      eventDialog: {
        show: false,
        saveLoading: false,
        event: {}
      },

      addTeamDialog: {
        show: false,
        loading: false,
        team: null
      },

      deleteTeamDialog: {
        show: false,
        loading: false,
        teamId: -1
      },

      snackbar: {
        show: false,
        text: ""
      },
      pageLoaded: false
    };
  },

  mounted() {
    this.pageLoaded = false;
    this.getEvent().then(() => {
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

  methods: {
    getEvent() {
      const id = this.$route.params.event;
      return this.$http
        .get(`/api/v1/events/${id}?include_teams=1`)
        .then(resp => {
          this.event = resp.data;
          if (!this.event.teams) {
            this.event.teams = [];
          }
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
      delete newEvent.teams;
      delete newEvent.id;
      const eventId = event.id;
      this.$http
        .put(`/api/v1/events/${eventId}`, newEvent)
        .then(resp => {
          console.log("EDITED", resp);
          this.eventDialog.show = false;
          this.eventDialog.saveLoading = false;
          this.pageLoaded = false;
          this.getEvent().then(() => (this.pageLoaded = true));
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

    cancelAddTeam() {
      this.addTeamDialog.loading = false;
      this.addTeamDialog.show = false;
      this.addTeamDialog.team = null;
    },

    addTeam() {
      const eventId = this.$route.params.event;
      let teamId = this.addTeamDialog.team.id;
      const idx = this.event.teams.findIndex(ev_te => ev_te.team_id === teamId);
      if (idx > -1) {
        this.addTeamDialog.loading = false;
        this.addTeamDialog.show = false;
        this.addTeamDialog.team = null;
        this.showSnackbar(this.$t("events.teams.team-on-event"));
        return;
      }

      this.$http
        .post(`/api/v1/events/${eventId}/teams/${teamId}`)
        .then(() => {
          this.showSnackbar(this.$t("events.teams.team-added"));
          this.addTeamDialog.loading = false;
          this.addTeamDialog.show = false;
          this.addTeamDialog.team = null;
          this.pageLoaded = false;
          this.getEvent().then(() => (this.pageLoaded = true));
        })
        .catch(err => {
          console.log(err);
          this.addTeamDialog.loading = false;
          if (err.response.status == 422) {
            this.showSnackbar(this.$t("events.teams.error-team-assigned"));
          } else {
            this.showSnackbar(this.$t("events.teams.error-adding-team"));
          }
        });
    },

    deleteTeam() {
      let id = this.deleteTeamDialog.teamId;
      const idx = this.event.teams.findIndex(ev_te => ev_te.team_id === id);
      this.deleteTeamDialog.loading = true;
      const eventId = this.$route.params.event;
      this.$http
        .delete(`/api/v1/events/${eventId}/teams/${id}`)
        .then(resp => {
          console.log("REMOVED", resp);
          this.deleteTeamDialog.show = false;
          this.deleteTeamDialog.loading = false;
          this.deleteTeamDialog.teamId = -1;
          this.event.teams.splice(idx, 1);
          this.showSnackbar(this.$t("events.teams.team-removed"));
        })
        .catch(err => {
          console.log(err);
          this.deleteTeamDialog.loading = false;
          this.showSnackbar(this.$t("events.teams.error-removing-team"));
        });
    },

    showDeleteTeamDialog(teamId) {
      this.deleteTeamDialog.teamId = teamId;
      this.deleteTeamDialog.show = true;
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
