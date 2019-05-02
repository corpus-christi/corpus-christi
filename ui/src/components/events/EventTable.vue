<template>
  <div>
    <v-layout justify-center>
      <v-flex shrink class="mb-2">
        <h1 class="hidden-sm-and-up">{{ $t("events.header") }}</h1>
      </v-flex>
    </v-layout>
    <v-toolbar class="pa-1" extension-height="64px">
      <v-layout justify-space-between>
        <v-flex shrink align-self-center>
          <v-toolbar-title class="hidden-xs-only">{{
            $t("events.header")
          }}</v-toolbar-title>
        </v-flex>
        <v-spacer></v-spacer>
        <v-text-field
          class="max-width-250 mr-2"
          v-model="search"
          append-icon="search"
          v-bind:label="$t('actions.search')"
          single-line
          hide-details
          data-cy="form-search"
        ></v-text-field>
        <v-flex shrink justify-self-end>
          <v-btn
            class="hidden-xs-only mr-2"
            color="primary"
            raised
            v-on:click.stop="newEvent"
            data-cy="add-event"
          >
            <v-icon dark>add</v-icon>
            <span class="mr-1"> {{ $t("actions.add-event") }} </span>
          </v-btn>
          <v-btn
            class="hidden-sm-and-up"
            color="primary"
            raised
            fab
            v-on:click.stop="newEvent"
            data-cy="add-event-small"
          >
            <v-icon dark>add</v-icon>
          </v-btn>
        </v-flex>
      </v-layout>
      <v-layout row slot="extension" justify-space-between align-center>
        <v-flex>
          <v-select
            class="max-width-250 mr-2"
            hide-details
            solo
            single-line
            :items="viewOptions"
            v-model="viewStatus"
            data-cy="view-status-select"
          >
          </v-select>
        </v-flex>
        <v-flex shrink>
          <v-switch
            hide-details
            v-model="viewPast"
            data-cy="view-past-switch"
            v-bind:label="$t('actions.view-past')"
          >
          </v-switch>
        </v-flex>
      </v-layout>
    </v-toolbar>
    <v-data-table
      :headers="headers"
      :rows-per-page-items="rowsPerPageItem"
      :items="visibleEvents"
      :search="search"
      :loading="tableLoading"
      :pagination.sync="paginationInfo"
      must-sort
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <!-- TODO: Add icons for past, upcoming, etc. -->
        <td>
          <v-icon
            v-if="eventOngoing(props.item)"
            slot="badge"
            small
            justify-space-around
            color="secondary"
            >autorenew</v-icon
          >
        </td>
        <td class="hover-hand" v-on:click="navigateToEvent(props.item.id)">
          <span> {{ props.item.title }}</span>
        </td>
        <td class="hover-hand" v-on:click="navigateToEvent(props.item.id)">
          {{ getDisplayDate(props.item.start) }}
        </td>
        <td class="hover-hand" v-on:click="navigateToEvent(props.item.id)">
          {{ getDisplayLocation(props.item.location) }}
        </td>
        <td>
          <template v-if="props.item.active">
            <v-tooltip bottom>
              <v-btn
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="editEvent(props.item)"
                data-cy="edit"
              >
                <v-icon small>edit</v-icon>
              </v-btn>
              <span>{{ $t("actions.edit") }}</span>
            </v-tooltip>
            <v-tooltip bottom>
              <v-btn
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="duplicate(props.item)"
                data-cy="duplicate"
              >
                <v-icon small>filter_none</v-icon>
              </v-btn>
              <span>{{ $t("actions.duplicate") }}</span>
            </v-tooltip>
            <v-tooltip bottom>
              <v-btn
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="confirmArchive(props.item)"
                data-cy="archive"
              >
                <v-icon small>archive</v-icon>
              </v-btn>
              <span>{{ $t("actions.tooltips.archive") }}</span>
            </v-tooltip>
          </template>
          <template v-else>
            <v-tooltip bottom v-if="!props.item.active">
              <v-btn
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="unarchive(props.item)"
                :loading="props.item.id < 0"
                data-cy="unarchive"
              >
                <v-icon small>undo</v-icon>
              </v-btn>
              <span>{{ $t("actions.tooltips.activate") }}</span>
            </v-tooltip>
          </template>
        </td>
      </template>
    </v-data-table>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false">
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>

    <!-- New/Edit dialog -->
    <v-dialog v-model="eventDialog.show" max-width="500px" persistent>
      <event-form
        v-bind:editMode="eventDialog.editMode"
        v-bind:initialData="eventDialog.event"
        v-bind:saveLoading="eventDialog.saveLoading"
        v-bind:addMoreLoading="eventDialog.addMoreLoading"
        v-on:cancel="cancelEvent"
        v-on:save="saveEvent"
        v-on:addAnother="addAnother"
      />
    </v-dialog>

    <!-- Archive dialog -->
    <v-dialog v-model="archiveDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{ $t("events.confirm-archive") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelArchive"
            color="secondary"
            flat
            data-cy="cancel-archive"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="archiveEvent"
            color="primary"
            raised
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import EventForm from "./EventForm";
import { mapGetters } from "vuex";
export default {
  name: "EventTable",
  components: { "event-form": EventForm },
  data() {
    return {
      active: 0,
      rowsPerPageItem: [
        10,
        15,
        25,
        { text: "$vuetify.dataIterator.rowsPerPageAll", value: -1 }
      ],
      paginationInfo: {
        sortBy: "start", //default sorted column
        rowsPerPage: 10,
        page: 1
      },
      tableLoading: true,
      events: [],
      eventDialog: {
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        event: {}
      },
      archiveDialog: {
        show: false,
        eventId: -1,
        loading: false
      },
      search: "",

      imageId: -1, // not the best way to do this, but works for now -- maybe rewrite?
      oldImageId: -1,

      snackbar: {
        show: false,
        text: ""
      },
      addMore: false,
      viewStatus: "viewActive",
      viewPast: false,
      windowSize: {
        x: 0,
        y: 0,
        screen
      }
    };
  },
  computed: {
    headers() {
      return [
        { text: "", sortable: false, width: "5%" },
        { text: this.$t("events.title"), value: "title" },
        { text: this.$t("events.start-time"), value: "start" },
        { text: this.$t("events.event-location"), value: "location_name" },
        { text: this.$t("actions.header"), sortable: false }
      ];
    },

    viewOptions() {
      return [
        { text: this.$t("actions.view-active"), value: "viewActive" },
        { text: this.$t("actions.view-archived"), value: "viewArchived" },
        { text: this.$t("actions.view-all"), value: "viewAll" }
      ];
    },

    visibleEvents() {
      let list = this.events;
      if (!this.viewPast) {
        let today = new Date();
        list = this.events.filter(ev => new Date(ev.end) >= today);
      }
      if (this.viewStatus == "viewActive") {
        list = list.filter(ev => ev.active);
      } else if (this.viewStatus == "viewArchived") {
        list = list.filter(ev => !ev.active);
      }
      return list;
    },

    ...mapGetters(["currentLanguageCode"])
  },
  methods: {
    activateEventDialog(event = {}, editMode = false) {
      this.eventDialog.editMode = editMode;
      this.eventDialog.event = event;
      this.eventDialog.show = true;
    },

    editEvent(event) {
      this.activateEventDialog({ ...event }, true);
    },

    activateArchiveDialog(eventId) {
      this.archiveDialog.show = true;
      this.archiveDialog.eventId = eventId;
    },

    confirmArchive(event) {
      this.activateArchiveDialog(event.id);
    },

    duplicate(event) {
      //TODO loading logic
      let id = event.id;
      this.$http
        .get(
          `/api/v1/events/${id}?include_teams=1&include_assets=1&include_persons=1`
        )
        .then(resp => {
          const copyEvent = JSON.parse(JSON.stringify(resp.data));
          copyEvent.start = new Date(copyEvent.start);
          copyEvent.end = new Date(copyEvent.end);
          const startDate = copyEvent.start.toDateString();
          const endDate = copyEvent.end.toDateString();
          if (startDate != endDate) {
            const diff = copyEvent.end - copyEvent.start;
            copyEvent.dayDuration = Math.ceil(diff / 86400000);
          }
          copyEvent.start = new Date(copyEvent.start).getTime();
          copyEvent.end = new Date(copyEvent.end).getTime();
          copyEvent.start %= 86400000; //ms in a day
          copyEvent.end %= 86400000; //ms in a day
          delete copyEvent.id;
          this.activateEventDialog(copyEvent);
        })
        .catch(err => console.log("DUPLICATE ERROR", err));
    },

    archiveEvent() {
      console.log("Archived event");
      this.archiveDialog.loading = true;
      const eventId = this.archiveDialog.eventId;
      const idx = this.events.findIndex(ev => ev.id === eventId);
      this.$http
        .delete(`/api/v1/events/${eventId}`)
        .then(resp => {
          console.log("ARCHIVE", resp);
          this.events[idx].active = false;
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          this.showSnackbar(this.$t("events.event-archived"));
        })
        .catch(err => {
          console.error("ARCHIVE FALURE", err.response);
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          this.showSnackbar(this.$t("events.error-archiving-event"));
        });
    },

    unarchive(event) {
      const idx = this.events.findIndex(ev => ev.id === event.id);
      const patchId = event.id;
      event.id *= -1; // to show loading spinner
      this.$http
        .patch(`/api/v1/events/${patchId}`, { active: true })
        .then(resp => {
          console.log("UNARCHIVED", resp);
          Object.assign(this.events[idx], resp.data);
          this.showSnackbar(this.$t("events.event-unarchived"));
        })
        .catch(err => {
          console.error("UNARCHIVE FALURE", err.response);
          this.showSnackbar(this.$t("events.error-unarchiving-event"));
        });
    },

    cancelArchive() {
      this.archiveDialog.show = false;
    },

    newEvent() {
      this.activateEventDialog();
    },

    clearEvent() {
      this.addMore = false;
      this.eventDialog.saveLoading = false;
      this.eventDialog.addMoreLoading = false;
      this.eventDialog.event = {};
    },

    cancelEvent() {
      this.addMore = false;
      this.eventDialog.show = false;
      this.eventDialog.saveLoading = false;
      this.eventDialog.addMoreLoading = false;
    },

    addAnother(event) {
      this.addMore = true;
      this.eventDialog.addMoreLoading = true;
      this.saveEvent(event);
    },

    save(event) {
      this.eventDialog.saveLoading = true;
      this.saveEvent(event);
    },

    async saveEvent(event) {
      if (event.location) {
        event.location_id = event.location.id;
      }
      delete event.images;

      let newEvent = JSON.parse(JSON.stringify(event));
      const oldImageId = await this.getOldImageId(event.id);
      const newImageId = newEvent.newImageId;
      delete newEvent.newImageId;
      delete newEvent.location;
      delete newEvent.dayDuration;
      delete newEvent.id;
      delete newEvent.aggregate;
      delete newEvent.attendance;

      console.log(newImageId, oldImageId);

      if (this.eventDialog.editMode) {
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
                console.log("IMAGEEVENT EDITED", resp);
                this.$http
                  .put(`/api/v1/events/${eventId}`, newEvent)
                  .then(resp => {
                    console.log("EDITED", resp);
                    this.refreshEventsTable();
                    this.cancelEvent();
                    this.showSnackbar(this.$t("events.event-edited"));
                  })
                  .catch(err => {
                    console.error("PUT FALURE", err.response);
                    this.eventDialog.saveLoading = false;
                    this.showSnackbar(this.$t("events.error-editing-event"));
                  });
              })
              .catch(err => {
                console.error("ERROR PUTTING IMAGE ON EVENT", err.response);
                this.eventDialog.saveLoading = false;
                this.showSnackbar(this.$t("events.error-editing-event"));
              });
          } else {
            // an image should be added (POST)
            this.$http
              .post(`/api/v1/events/${eventId}/images/${newImageId}`)
              .then(resp => {
                console.log("IMAGEEVENT EDITED", resp);
                this.$http
                  .put(`/api/v1/events/${eventId}`, newEvent)
                  .then(resp => {
                    console.log("EDITED", resp);
                    this.refreshEventsTable();
                    this.cancelEvent();
                    this.showSnackbar(this.$t("events.event-edited"));
                  })
                  .catch(err => {
                    console.error("PUT FALURE", err.response);
                    this.eventDialog.saveLoading = false;
                    this.showSnackbar(this.$t("events.error-editing-event"));
                  });
              })
              .catch(err => {
                console.error("ERROR ADDING IMAGE TO EVENT", err.response);
                this.eventDialog.saveLoading = false;
                this.showSnackbar(this.$t("events.error-editing-event"));
              });
          }
        } else {
          // either an image was deleted, or no images were added
          if (oldImageId) {
            // an image should be deleted (DELETE)
            this.$http
              .delete(`/api/v1/events/${eventId}/images/${oldImageId}`)
              .then(resp => {
                console.log("IMAGEEVENT EDITED", resp);
                this.$http
                  .put(`/api/v1/events/${eventId}`, newEvent)
                  .then(resp => {
                    console.log("EDITED", resp);
                    this.refreshEventsTable();
                    this.cancelEvent();
                    this.showSnackbar(this.$t("events.event-edited"));
                  })
                  .catch(err => {
                    console.error("PUT FALURE", err.response);
                    this.eventDialog.saveLoading = false;
                    this.showSnackbar(this.$t("events.error-editing-event"));
                  });
              })
              .catch(err => {
                console.error("ERROR DELETING IMAGE FROM EVENT", err.response);
                this.eventDialog.saveLoading = false;
                this.showSnackbar(this.$t("events.error-editing-event"));
              });
          } else {
            // no image call necessary (NOTHING)
            this.$http
              .put(`/api/v1/events/${eventId}`, newEvent)
              .then(resp => {
                console.log("EDITED", resp);
                this.refreshEventsTable();
                this.cancelEvent();
                this.showSnackbar(this.$t("events.event-edited"));
              })
              .catch(err => {
                console.error("PUT FALURE", err.response);
                this.eventDialog.saveLoading = false;
                this.showSnackbar(this.$t("events.error-editing-event"));
              });
          }
        }
      } else {
        let newTeams = newEvent.teams;
        delete newEvent.teams;
        let newPersons = newEvent.persons;
        delete newEvent.persons;
        let newAssets = newEvent.assets;
        delete newEvent.assets;
        this.$http
          .post("/api/v1/events/", newEvent)
          .then(resp => {
            let promises = this.getDuplicationPromises(
              resp.data.id,
              newTeams,
              newPersons,
              newAssets,
              newImageId
            );
            if (promises) {
              Promise.all(promises).then(values => {
                console.log(values);
                return resp;
              });
            }
            return resp;
          })
          .then(resp => {
            console.log("ADDED", resp);
            // this.events.push(resp.data);
            if (this.addMore) {
              this.clearEvent();
            } else {
              this.cancelEvent();
            }
            this.showSnackbar(this.$t("events.event-added"));
            this.refreshEventsTable();
          })
          .catch(err => {
            console.error("POST FAILURE", err.response);
            this.eventDialog.saveLoading = false;
            this.eventDialog.addMoreLoading = false;
            this.showSnackbar(this.$t("events.error-adding-event"));
          });
      }
    },

    refreshEventsTable() {
      this.tableLoading = true;
      this.$http
        .get("/api/v1/events/?return_group=all&include_images=1")
        .then(resp => {
          this.events = resp.data;
          this.tableLoading = false;
        });
      this.onResize();
    },

    getDuplicationPromises(
      eventId,
      newTeams,
      newPersons,
      newAssets,
      newImageId
    ) {
      if (!newTeams && !newPersons && !newAssets && !newImageId) return null;
      let promises = [];
      if (newTeams) {
        for (let t of newTeams) {
          let promise = this.postEventTeam(eventId, t.team_id);
          promises.push(promise);
        }
      }
      if (newPersons) {
        for (let p of newPersons) {
          let promise = this.postEventPerson(
            eventId,
            p.person_id,
            p.description
          );
          promises.push(promise);
        }
      }
      if (newAssets) {
        for (let a of newAssets) {
          let promise = this.postEventAsset(eventId, a.asset_id);
          promises.push(promise);
        }
      }
      if (newImageId) {
        let promise = this.postImageEvent(eventId, newImageId);
        promises.push(promise);
      }
      return promises;
    },

    postEventTeam(eventId, teamId) {
      return this.$http.post(`/api/v1/events/${eventId}/teams/${teamId}`);
    },
    postEventAsset(eventId, assetId) {
      return this.$http.post(`/api/v1/events/${eventId}/assets/${assetId}`);
    },
    postEventPerson(eventId, personId, description) {
      return this.$http.post(
        `/api/v1/events/${eventId}/individuals/${personId}`,
        { description }
      );
    },
    postImageEvent(eventId, newImageId) {
      return this.$http.post(`/api/v1/events/${eventId}/images/${newImageId}`);
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

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },

    getDisplayDate(dateString) {
      let date = new Date(dateString);
      return date.toLocaleTimeString(this.currentLanguageCode, {
        year: "numeric",
        month: "numeric",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      });
    },

    getDisplayLocation(location, length = 20) {
      if (location && location.description) {
        let name = location.description;
        if (name && name.length && name.length > 0) {
          if (name.length > length) {
            return `${name.substring(0, length - 3)}...`;
          }
          return name;
        }
      }
      return name;
    },

    navigateToEvent(id) {
      this.$router.push({ path: "/event/" + id });
    },

    eventOngoing(event) {
      let start = new Date(event.start);
      let end = new Date(event.end);
      return start <= Date.now() && Date.now() <= end;
    },

    onResize() {
      this.windowSize = { x: window.innerWidth, y: window.innerHeight };
      if (this.windowSize.x <= 960) {
        this.windowSize.small = true;
      } else {
        this.windowSize.small = false;
      }
    }
  },

  mounted() {
    this.refreshEventsTable();
  }
};
</script>

<style scoped>
.hover-hand {
  cursor: pointer;
}

.max-width-250 {
  max-width: 250px;
}
</style>
