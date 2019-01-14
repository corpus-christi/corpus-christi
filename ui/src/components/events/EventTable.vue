<template>
  <div>
    <v-toolbar class="pa-1">
      <v-layout align-center justify-space-between fill-height>
        <v-flex md2>
          <v-toolbar-title>{{ $t("events.title") }}</v-toolbar-title>
        </v-flex>
        <v-flex md2>
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="$t('actions.search')"
            single-line
            hide-details
            data-cy="form-search"
          ></v-text-field>
        </v-flex>
        <v-flex md3>
          <v-select
            hide-details
            solo
            single-line
            :items="viewOptions"
            v-model="viewStatus"
            data-cy="view-status-select"
          >
          </v-select>
        </v-flex>
        <v-flex shrink justify-self-end>
          <v-btn
            color="primary"
            raised
            v-on:click.stop="newEvent"
            data-cy="add-event"
          >
            <v-icon dark left>add</v-icon>
            {{ $t("actions.add-event") }}
          </v-btn>
        </v-flex>
      </v-layout>
    </v-toolbar>

    <v-data-table
      :headers="headers"
      :items="visibleEvents"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td
          class="hover-hand"
          v-on:click="$router.push({ path: '/events/' + props.item.id })"
        >
          {{ props.item.title }}
        </td>
        <td
          class="hover-hand"
          v-on:click="$router.push({ path: '/events/' + props.item.id })"
        >
          {{ getDisplayDate(props.item.start) }}
        </td>
        <td
          class="hover-hand"
          v-on:click="$router.push({ path: '/events/' + props.item.id })"
        >
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
                :loading="props.item.unarchiving"
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
        v-on:add-another="addAnotherEvent"
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
  mounted() {
    this.tableLoading = true;
    this.$http.get("/api/v1/events/?return_group=all").then(resp => {
      this.events = resp.data;
      this.tableLoading = false;
    });
    this.onResize();
  },

  data() {
    return {
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

      snackbar: {
        show: false,
        text: ""
      },
      viewStatus: "viewAll",

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
        { text: this.$t("events.title"), value: "title" },
        { text: this.$t("events.start-time"), value: "start" },
        { text: this.$t("events.event-location"), value: "location_name" },
        { text: this.$t("events.actions"), sortable: false }
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
      if (this.viewStatus == "viewActive") {
        return this.events.filter(ev => ev.active);
      } else if (this.viewStatus == "viewArchived") {
        return this.events.filter(ev => !ev.active);
      } else {
        return this.events;
      }
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
      const copyEvent = JSON.parse(JSON.stringify(event));
      copyEvent.start = new Date(copyEvent.start).getTime();
      copyEvent.start %= 86400000; //ms in a day
      copyEvent.end = new Date(copyEvent.end).getTime();
      copyEvent.end %= 86400000; //ms in a day
      delete copyEvent.id;
      this.activateEventDialog(copyEvent);
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
      const copyEvent = JSON.parse(JSON.stringify(event));
      event.unarchiving = true;
      copyEvent.active = true;
      const putId = copyEvent.id;
      delete copyEvent.id;
      delete copyEvent.location; //Temporary delete
      this.$http
        .put(`/api/v1/events/${putId}`, copyEvent)
        .then(resp => {
          console.log("UNARCHIVED", resp);
          delete event.unarchiving;
          Object.assign(this.events[idx], resp.data);
          this.showSnackbar(this.$t("events.event-unarchived"));
        })
        .catch(err => {
          delete event.unarchiving;
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

    cancelEvent() {
      this.eventDialog.show = false;
    },

    saveEvent(event) {
      this.eventDialog.saveLoading = true;
      event.location_id = event.location.id;
      let newEvent = JSON.parse(JSON.stringify(event));
      delete newEvent.location;
      delete newEvent.id;
      if (this.eventDialog.editMode) {
        const eventId = event.id;
        const idx = this.events.findIndex(ev => ev.id === event.id);
        this.$http
          .put(`/api/v1/events/${eventId}`, newEvent)
          .then(resp => {
            console.log("EDITED", resp);
            Object.assign(this.events[idx], newEvent);
            this.eventDialog.show = false;
            this.eventDialog.saveLoading = false;
            this.showSnackbar(this.$t("events.event-edited"));
          })
          .catch(err => {
            console.error("PUT FALURE", err.response);
            this.eventDialog.saveLoading = false;
            this.showSnackbar(this.$t("events.error-editing-event"));
          });
      } else {
        this.$http
          .post("/api/v1/events/", newEvent)
          .then(resp => {
            console.log("ADDED", resp);
            this.events.push(resp.data);
            this.eventDialog.show = false;
            this.eventDialog.saveLoading = false;
            this.showSnackbar(this.$t("events.event-added"));
          })
          .catch(err => {
            console.error("POST FAILURE", err.response);
            this.eventDialog.saveLoading = false;
            this.showSnackbar(this.$t("events.error-adding-event"));
          });
      }
    },

    addAnotherEvent(event) {
      this.eventDialog.addMoreLoading = true;
      event.location_id = event.location.id;
      let newEvent = JSON.parse(JSON.stringify(event));
      delete newEvent.location;
      this.$http
        .post("/api/v1/events/", event)
        .then(resp => {
          console.log("ADDED", resp);
          this.events.push(resp.data);
          this.eventDialog.show = false;
          this.eventDialog.saveLoading = false;
          this.showSnackbar(this.$t("events.event-added"));
        })
        .catch(err => {
          console.error("FAILURE", err.response);
          this.eventDialog.saveLoading = false;
          this.showSnackbar(this.$t("events.error-adding-event"));
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

    onResize() {
      this.windowSize = { x: window.innerWidth, y: window.innerHeight };
      if (this.windowSize.x <= 960) {
        this.windowSize.small = true;
      } else {
        this.windowSize.small = false;
      }
    }
  }
};
</script>

<style scoped>
.hover-hand {
  cursor: pointer;
}
</style>
