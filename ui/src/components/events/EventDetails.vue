<template>
  <div>
    <v-container fluid>
      <v-row>
        <v-col cols=12>
          <v-card>
            <template v-if="eventLoaded">
              <v-toolbar dark color="primary">
                <v-toolbar-title>
                  <span class="headline">{{ event.title }}</span>
                </v-toolbar-title>
                <v-spacer/>
                <v-btn
                  right
                  outlined
                  data-cy="edit-event"
                  @click="editEvent(event)"
                >
                  <v-icon left>edit</v-icon>{{ $t("actions.edit") }}
                </v-btn>
              </v-toolbar>
              <v-container fluid>
                <v-card-text>
                  <v-row>
                    <v-col cols=12 sm=6>
                      <div>
                        <b>{{ $t("events.attendance") }}: </b>
                        <span v-if="event.attendance != null">{{
                          event.attendance
                        }}</span>
                        <span v-else>{{ $t("events.attendance-none") }} </span>
                        <v-btn
                          icon
                          outlined
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
                      <div>{{ event.description }}</div>
                    </v-col>
                    <v-col cols=12 sm=6>
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
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-container>
              <v-card-actions>
                  <v-btn
                    ripple
                    color="primary"
                    data-cy="navigate-to-participants"
                    :to="'/event/' + $route.params.event + '/participants'"
                  >
                    <v-icon left>person</v-icon>{{
                      $t("events.participants.title")
                    }}
                  </v-btn>
              </v-card-actions>
            </template>
            <v-layout v-else justify-center height="500px">
              <div>
                <v-progress-circular
                  indeterminate
                  color="primary"
                ></v-progress-circular>
              </div>
            </v-layout>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols=12 md=6 lg=4>
          <event-item-details
            item="team"
            :loaded="teamsLoaded"
            :items="event.teams"
            v-on:item-added="addTeam"
            v-on:item-deleted="deleteTeam"
          />
        </v-col>
        <v-col cols=12 md=6 lg=4>
          <event-item-details
            item="person"
            :loaded="personsLoaded"
            :items="event.persons"
            v-on:item-added="addPerson"
            v-on:item-deleted="deletePerson"
          />
        </v-col>
        <v-col cols=12 md=6 lg=4>
          <event-item-details
            item="group"
            :loaded="groupsLoaded"
            :items="event.groups"
            v-on:item-added="addGroup"
            v-on:item-deleted="deleteGroup"
          />
        </v-col>
      </v-row>
    </v-container>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn @click="snackbar.show = false" data-cy="close-snackbar">
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
        addImageField
        endDateTimeField
        startDateTimeField
        v-bind:titleLabel="$t('events.title')"
        v-bind:descriptionLabel="$t('events.event-description')"
        v-bind:locationLabel="$t('events.event-location')"
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
  </div>
</template>

<script>
import CustomForm from "../CustomForm";
import { mapGetters } from "vuex";
import EventItemDetails from "./EventItemDetails";
import EventAttendanceForm from "./EventAttendanceForm";
import arcoPlaceholder from "../../../assets/arco-placeholder.jpg";

export default {
  name: "EventDetails",
  components: {
    "event-form": CustomForm,
    "event-item-details": EventItemDetails,
    "event-attendance-form": EventAttendanceForm,
  },

  data() {
    return {
      event: {},
      eventDialog: {
        show: false,
        saveLoading: false,
        event: {},
      },

      attendanceDialog: {
        show: false,
        saving: false,
        number: null,
      },

      snackbar: {
        show: false,
        text: "",
      },
      eventLoaded: false,
      teamsLoaded: false,
      groupsLoaded: false,
      assetsLoaded: false,
      personsLoaded: false,
      arcoPlaceholder,
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

    ...mapGetters(["currentLanguageCode"]),
  },

  methods: {

    getEvent() {
      const id = this.$route.params.event;
      return this.$http
        .get(
          `/api/v1/events/${id}?include_teams=1&include_assets=1&include_persons=1&include_images=1&include_groups=1`
        )
        .then((resp) => {
          this.event = resp.data;
          this.event.teams = !this.event.teams
            ? []
            : this.event.teams.map((t) => t.team);
          this.event.assets = !this.event.assets
            ? []
            : this.event.assets.map((a) => a.asset);
          this.event.groups = !this.event.groups
            ? []
            : this.event.groups
                .filter(function (g) {
                  // make sure the group is active
                  // ateamListnd the group has an active relationship to the event
                  if (g.group) {
                    return g.active && g.group.active;
                  }
                  return false;
                })
                .map((g) => g.group);
          // conserve description on EventPersons
          this.event.persons = !this.event.persons
            ? []
            : this.event.persons.map((p) =>
                Object.assign(p, { id: p.person_id })
              );
        });
    },

    addTeam(data) {
      console.log(data);
      const eventId = this.$route.params.event;
      let teamId = data.item.id;
      const idx = this.event.teams.findIndex((t) => t.id === teamId);
      if (idx > -1) {
        this.showSnackbar(this.$t("teams.team-on-event"));
        return;
      }

      this.$http
        .post(`/api/v1/events/${eventId}/teams/${teamId}`)
        .then(() => {
          this.showSnackbar(this.$t("teams.team-added"));
          this.event.teams.push(data.item);
        })
        .catch((err) => {
          console.log(err);
          if (err.response.status === 422) {
            this.showSnackbar(this.$t("teams.error-team-assigned"));
          } else {
            this.showSnackbar(this.$t("teams.error-adding-team"));
          }
        });
    },

    deleteTeam(data) {
      console.log(data);
      const eventId = this.$route.params.event;
      let id = data.itemId;
      const idx = this.event.teams.findIndex((t) => t.id === id);
      this.$http
        .delete(`/api/v1/events/${eventId}/teams/${id}`)
        .then((resp) => {
          console.log("REMOVED", resp);
          this.event.teams.splice(idx, 1); //TODO maybe fix me?
          this.showSnackbar(this.$t("teams.team-removed"));
        })
        .catch((err) => {
          console.log(err);
          this.showSnackbar(this.$t("teams.error-removing-team"));
        });
    },

    addPerson(data) {
      const eventId = this.$route.params.event;
      let personData = data.item;
      let personId = personData.id;
      const idx = this.event.persons.findIndex((p) => p.id === personId);
      if (!data.editMode && idx > -1) {
        this.showSnackbar(this.$t("events.persons.person-on-event"));
      }
      let body = { description: data.description };
      let promise;
      if (data.editMode) {
        promise = this.$http.patch(
          `/api/v1/events/${eventId}/individuals/${personId}`,
          body
        );
      } else {
        promise = this.$http.post(
          `/api/v1/events/${eventId}/individuals/${personId}`,
          body
        );
      }
      promise
        .then(() => {
          if (data.editMode) {
            this.showSnackbar(this.$t("events.persons.person-edited"));
          } else {
            this.showSnackbar(this.$t("events.persons.person-added"));
          }
          if (!data.editMode) {
            let eventPerson = {id: personId, person_id: personId, event_id: eventId, person: personData, description: data.description };
            this.event.persons.push(eventPerson);
          } else {
            this.event.persons[idx].description = data.description;
          }
      })
      .catch((err) => {
        console.log(err);
        if (err.response.status === 422) {
          this.showSnackbar(this.$t("events.persons.error-person-assigned"));
        } else {
          this.showSnackbar(this.$t("events.persons.error-adding-person"));
        }
      });
    },

    deletePerson(data) {
        const eventId = this.$route.params.event;
        let id = data.itemId;
        const idx = this.event.persons.findIndex((p) => p.id === id)
        this.$http
        .delete(`/api/v1/events/${eventId}/individuals/${id}`)
        .then((resp) => {
          console.log("REMOVED", resp);
          this.event.persons.splice(idx, 1); //TODO maybe fix me?
          this.showSnackbar(this.$t("events.persons.person-removed"));
        })
        .catch((err) => {
          console.log(err);
          this.showSnackbar(this.$t("events.persons.error-removing-person"));
        });
    },

    addAsset(data) {
      const eventId = this.$route.params.event;
      let assetId = data.asset.id;
      const idx = this.event.assets.findIndex((t) => t.id === assetId);
      if (idx > -1) {
        this.showSnackbar(this.$t("assets.asset-on-event"));
        return;
      }

      this.$http
        .post(`/api/v1/events/${eventId}/assets/${assetId}`)
        .then(() => {
          this.showSnackbar(this.$t("assets.asset-added"));
          this.event.assets.push(data.asset);
        })
        .catch((err) => {
          console.log(err);
          if (err.response.status === 422) {
            this.showSnackbar(this.$t("assets.error-asset-assigned"));
          } else {
            this.showSnackbar(this.$t("assets.error-adding-asset"));
          }
        });
    },

    deleteAsset(data) {
      const eventId = this.$route.params.event;
      let id = data.assetId;
      const idx = this.event.teams.findIndex((a) => a.id === id);
      this.$http
        .delete(`/api/v1/events/${eventId}/assets/${id}`)
        .then((resp) => {
          console.log("REMOVED", resp);
          this.event.assets.splice(idx, 1); //TODO maybe fix me?
          this.showSnackbar(this.$t("assets.asset-removed"));
        })
        .catch((err) => {
          console.log(err);
          this.showSnackbar(this.$t("assets.error-removing-asset"));
        });
    },

    addGroup(data) {
      const eventId = this.$route.params.event;
      let groupId = data.item.id;
      const idx = this.event.groups.findIndex((t) => t.id === groupId);
      if (idx > -1) {
        this.showSnackbar(this.$t("groups-group-on-event"));
        return;
      }

      this.$http
        .post(`/api/v1/events/${eventId}/groups/${groupId}`)
        .then(() => {
          this.showSnackbar(this.$t("groups.group-added"));
          this.event.groups.push(data.item);
        })
        .catch((err) => {
          console.log(err);
          if (err.response.status === 422) {
            this.showSnackbar(this.$t("groups.error-group-assigned"));
          } else {
            this.showSnackbar(this.$t("groups.error-adding-group"));
          }
        });
    },

    deleteGroup(data) {
      const eventId = this.$route.params.event;
      let id = data.itemId;
      const idx = this.event.groups.findIndex((t) => t.id === id);
      this.$http
        .delete(`/api/v1/events/${eventId}/groups/${id}`)
        .then((resp) => {
          console.log("REMOVED", resp);
          this.event.groups.splice(idx, 1); //TODO maybe fix me?
          this.showSnackbar(this.$t("groups.group-removed"));
        })
        .catch((err) => {
          console.log(err);
          this.showSnackbar(this.$t("groups.error-removing-group"));
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
            .then((resp) => {
              console.log("PUTTED", resp.data);
              this.$http
                .put(`/api/v1/events/${eventId}`, newEvent)
                .then((resp) => {
                  console.log("EDITED", resp);
                  this.eventDialog.show = false;
                  this.eventDialog.saveLoading = false;
                  this.eventLoaded = false;
                  this.getEvent().then(() => (this.eventLoaded = true));
                  this.showSnackbar(this.$t("events.event-edited"));
                })
                .catch((err) => {
                  console.error("PUT FALURE", err.response);
                  this.eventDialog.saveLoading = false;
                  this.showSnackbar(this.$t("events.error-editing-event"));
                });
            })
            .catch((err) => {
              console.error("ERROR PUTTING IMAGEEVENT", err.response);
              this.eventDialog.saveLoading = false;
              this.showSnackbar(this.$t("events.error-editing-event"));
            });
        } else {
          // an image should be added (POST)
          this.$http
            .post(`/api/v1/events/${eventId}/images/${newImageId}`)
            .then((resp) => {
              console.log("POSTED", resp.data);
              this.$http
                .put(`/api/v1/events/${eventId}`, newEvent)
                .then((resp) => {
                  console.log("EDITED", resp);
                  this.eventDialog.show = false;
                  this.eventDialog.saveLoading = false;
                  this.eventLoaded = false;
                  this.getEvent().then(() => (this.eventLoaded = true));
                  this.showSnackbar(this.$t("events.event-edited"));
                })
                .catch((err) => {
                  console.error("PUT FALURE", err.response);
                  this.eventDialog.saveLoading = false;
                  this.showSnackbar(this.$t("events.error-editing-event"));
                });
            })
            .catch((err) => {
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
            .then((resp) => {
              console.log("DELETED", resp.data);
              this.$http
                .put(`/api/v1/events/${eventId}`, newEvent)
                .then((resp) => {
                  console.log("EDITED", resp);
                  this.eventDialog.show = false;
                  this.eventDialog.saveLoading = false;
                  this.eventLoaded = false;
                  this.getEvent().then(() => (this.eventLoaded = true));
                  this.showSnackbar(this.$t("events.event-edited"));
                })
                .catch((err) => {
                  console.error("PUT FALURE", err.response);
                  this.eventDialog.saveLoading = false;
                  this.showSnackbar(this.$t("events.error-editing-event"));
                });
            })
            .catch((err) => {
              console.error("ERROR DELETING IMAGEEVENT", err.response);
              this.eventDialog.saveLoading = false;
              this.showSnackbar(this.$t("events.error-editing-event"));
            });
        } else {
          // nothing should happen
          this.$http
            .put(`/api/v1/events/${eventId}`, newEvent)
            .then((resp) => {
              console.log("EDITED", resp);
              this.eventDialog.show = false;
              this.eventDialog.saveLoading = false;
              this.eventLoaded = false;
              this.getEvent().then(() => (this.eventLoaded = true));
              this.showSnackbar(this.$t("events.event-edited"));
            })
            .catch((err) => {
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
        .then((resp) => {
          if (resp.data.images && resp.data.images.length > 0) {
            return resp.data.images[0].image_id;
          } else {
            return null;
          }
        })
        .catch((err) => {
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
        .then((resp) => {
          console.log(resp);
          this.event.attendance = resp.data.attendance;
          this.closeAttendanceDialog();
        })
        .catch((err) => {
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
        minute: "2-digit",
      });
    },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },
  },
};
</script>

<style scoped>
.multi-line {
  white-space: pre;
}
</style>
