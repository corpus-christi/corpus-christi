<template>
  <v-layout column>
    <v-layout row wrap>
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
              <v-layout row wrap>
                <v-flex xs12 sm6>
                  <div>
                    <b>{{ $t("events.attendance") }}: </b>
                    <span v-if="event.attendance != null">{{
                      event.attendance
                    }}</span>
                    <span v-else>{{ $t("events.attendance-none") }}</span>
                    <v-btn
                      icon
                      outline
                      small
                      color="primary"
                      data-cy="edit-attendance"
                      v-on:click="openAttendanceDialog()"
                    >
                      <v-icon small color="primary">edit</v-icon>
                    </v-btn>
                  </div>
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
                  <div class="mt-2 mb-2">{{ event.description }}</div>
                </v-flex>
                <v-flex xs12 sm6>
                  <!-- Image -->
                  <template v-if="event.images && event.images.length > 0">
                    <v-img
                      max-height="400px"
                      class="image picture"
                      :src="fetchImage"
                    >
                    </v-img>
                  </template>

                  <!-- Placeholder if no image uploaded -->
                  <template v-else>
                    <v-img class="picture" :src="arcoPlaceholder"> </v-img>
                  </template>
                </v-flex>
              </v-layout>
            </v-card-text>
            <v-card-actions>
              <v-layout justify-space-between wrap>
                <v-btn
                  flat
                  ripple
                  color="primary"
                  data-cy="navigate-to-participants"
                  :to="'/event/' + $route.params.event + '/participants'"
                >
                  <v-icon>person</v-icon>&nbsp;{{
                    $t("events.participants.title")
                  }}
                </v-btn>
              </v-layout>
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
    </v-layout>

    <v-layout row wrap>
      <v-flex xs12 lg6>
        <v-layout column>
          <v-flex>
            <event-team-details
              :teams="event.teams"
              :loaded="teamsLoaded"
              v-on:snackbar="showSnackbar($event)"
              v-on:team-added="reloadTeams()"
            ></event-team-details>
          </v-flex>
          <v-flex>
            <event-person-details
              :persons="event.persons"
              :loaded="personsLoaded"
              v-on:snackbar="showSnackbar($event)"
              v-on:person-added="reloadPersons()"
            ></event-person-details>
          </v-flex>
        </v-layout>
      </v-flex>
      <v-flex xs12 lg6>
        <v-layout column>
          <v-flex>
            <event-asset-details
              :assets="event.assets"
              :loaded="assetsLoaded"
              v-on:snackbar="showSnackbar($event)"
              v-on:asset-added="reloadAssets()"
            ></event-asset-details>
          </v-flex>
          <v-flex>
            <event-group-details
              :groups="event.groups"
              :loaded="groupsLoaded"
              v-on:snackbar="showSnackbar($event)"
              v-on:group-added="reloadGroups()"
            ></event-group-details>
          </v-flex>
        </v-layout>
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

    <!-- Attendance dialog -->
    <v-dialog v-model="attendanceDialog.show" persistent max-width="250px">
      <event-attendance-form
        v-bind:attendance="attendanceDialog.number"
        v-bind:saving="attendanceDialog.saving"
        v-on:cancel="attendanceDialog.show = false"
        v-on:save-attendance="saveAttendance($event)"
      ></event-attendance-form>
    </v-dialog>
  </v-layout>
</template>

<script>
import EventForm from "./EventForm";
import { mapGetters } from "vuex";
import EventTeamDetails from "./EventTeamDetails";
import EventAssetDetails from "./EventAssetDetails";
import EventPersonDetails from "./EventPersonDetails";
import EventGroupDetails from "./EventGroupDetails";
import EventAttendanceForm from "./EventAttendanceForm";
import arcoPlaceholder from "../../../assets/arco-placeholder.jpg";

export default {
  name: "EventDetails",
  components: {
    "event-form": EventForm,
    "event-team-details": EventTeamDetails,
    "event-asset-details": EventAssetDetails,
    "event-person-details": EventPersonDetails,
    "event-group-details": EventGroupDetails,
    "event-attendance-form": EventAttendanceForm
  },

  data() {
    return {
      event: {},
      eventDialog: {
        show: false,
        saveLoading: false,
        event: {}
      },

      attendanceDialog: {
        show: false,
        saving: false,
        number: null
      },

      snackbar: {
        show: false,
        text: ""
      },
      eventLoaded: false,
      teamsLoaded: false,
      groupsLoaded: false,
      assetsLoaded: false,
      personsLoaded: false,
      arcoPlaceholder
    };
  },

  mounted() {
    this.eventLoaded = false;
    this.teamsLoaded = false;
    this.groupsLoaded = false;
    this.assetsLoaded = false;
    this.personsLoaded = false;
    this.getEvent().then(() => {
      this.eventLoaded = true;
      this.teamsLoaded = true;
      this.groupsLoaded = true;
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

    fetchImage() {
      return `/api/v1/images/${this.event.images[0].image.id}?${Math.random()}`;
    },

    ...mapGetters(["currentLanguageCode"])
  },

  methods: {
    getEvent() {
      const id = this.$route.params.event;
      return this.$http
        .get(
          `/api/v1/events/${id}?include_teams=1&include_assets=1&include_persons=1&include_images=1&include_groups=1`
        )
        .then(resp => {
          this.event = resp.data;
          this.event.teams = !this.event.teams
            ? []
            : this.event.teams.map(t => t.team);
          this.event.assets = !this.event.assets
            ? []
            : this.event.assets.map(a => a.asset);
          this.event.groups = !this.event.groups
            ? []
            : this.event.groups.filter(function(g) {
                // make sure the group is active
                // and the group has an active relationship to the event
                if (g.group) {
                  return g.active && g.group.active;
                }
                return false;
              }).map(g => g.group);
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

    reloadGroups() {
      this.groupsLoaded = false;
      const id = this.$route.params.event;
      this.$http.get(`/api/v1/events/${id}?include_groups=1`).then(resp => {
        let eventData = resp.data;
        this.event.groups =
          (
            !eventData.groups ? [] : eventData.groups.filter(function(g) {
                // make sure the group is active
                // and the group has an active relationship to the event
                if (g.group) {
                  return g.active && g.group.active;
                }
                return false;
            }).map(g => g.group)
          );
        this.groupsLoaded = true;
      });
    },

    editEvent(event) {
      this.eventDialog.event = JSON.parse(JSON.stringify(event));
      this.eventDialog.show = true;
    },

    cancelEvent() {
      this.eventDialog.show = false;
    },

    async saveEvent(event) {
      this.eventDialog.saveLoading = true;
      if (event.location) {
        event.location_id = event.location.id;
      }
      let newEvent = JSON.parse(JSON.stringify(event));
      const oldImageId = await this.getOldImageId(event.id);
      const newImageId = newEvent.newImageId;
      delete newEvent.newImageId;
      delete newEvent.location;
      delete newEvent.assets;
      delete newEvent.teams;
      delete newEvent.groups;
      delete newEvent.persons;
      delete newEvent.dayDuration;
      delete newEvent.id;
      delete newEvent.images;
      const eventId = event.id;

      if (newImageId) {
        // a new image was added to the event
        if (oldImageId) {
          // an image should be updated (PUT)
          this.$http
            .put(
              `/api/v1/events/${eventId}/images/${newImageId}?old=${oldImageId}`
            )
            .then(resp => {
              console.log("PUTTED", resp.data);
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
            })
            .catch(err => {
              console.error("ERROR PUTTING IMAGEEVENT", err.response);
              this.eventDialog.saveLoading = false;
              this.showSnackbar(this.$t("events.error-editing-event"));
            });
        } else {
          // an image should be added (POST)
          this.$http
            .post(`/api/v1/events/${eventId}/images/${newImageId}`)
            .then(resp => {
              console.log("POSTED", resp.data);
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
            })
            .catch(err => {
              console.error("ERROR POSTING IMAGEEVENT", err.response);
              this.eventDialog.saveLoading = false;
              this.showSnackbar(this.$t("events.error-editing-event"));
            });
        }
      } else {
        // an image never existed or was deleted
        if (oldImageId) {
          // an image should be removed (DELETE)
          this.$http
            .delete(`/api/v1/events/${eventId}/images/${oldImageId}`)
            .then(resp => {
              console.log("DELETED", resp.data);
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
            })
            .catch(err => {
              console.error("ERROR DELETING IMAGEEVENT", err.response);
              this.eventDialog.saveLoading = false;
              this.showSnackbar(this.$t("events.error-editing-event"));
            });
        } else {
          // nothing should happen
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
        }
      }
    },

    async getOldImageId(id) {
      if (!id) {
        return null;
      }
      return await this.$http
        .get(`/api/v1/events/${id}?include_images=1`)
        .then(resp => {
          if (resp.data.images && resp.data.images.length > 0) {
            return resp.data.images[0].image_id;
          } else {
            return null;
          }
        })
        .catch(err => {
          console.error("ERROR FETCHING EVENT", err);
          return null;
        });
    },

    openAttendanceDialog() {
      this.attendanceDialog.show = true;
      this.attendanceDialog.saving = false;
      this.attendanceDialog.number = this.event.attendance;
    },

    closeAttendanceDialog() {
      this.attendanceDialog.show = false;
      this.attendanceDialog.saving = false;
      this.attendanceDialog.number = null;
    },

    saveAttendance(number) {
      const id = this.$route.params.event;
      this.$http
        .patch(`/api/v1/events/${id}`, { attendance: number })
        .then(resp => {
          console.log(resp);
          this.event.attendance = resp.data.attendance;
          this.closeAttendanceDialog();
        })
        .catch(err => {
          console.error("ATTENDANCE PATCH FAILURE", err.response);
          this.attendanceDialog.saving = false;
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

<style scoped>
.multi-line {
  white-space: pre;
}
</style>
