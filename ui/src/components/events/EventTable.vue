<template>
  <div>
    <v-toolbar>
      <v-toolbar-title>{{ $t("events.title") }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="search"
        v-bind:label="$t('actions.search')"
        single-line
        hide-details
      ></v-text-field>
      <v-spacer></v-spacer>

      <v-btn
        color="primary"
        raised
        v-on:click.stop="newEvent"
        data-cy="add-event"
      >
        <v-icon dark left>add</v-icon>
        {{ $t("actions.addevent") }}
      </v-btn>

    </v-toolbar>

    <v-data-table :headers="headers" :items="events" :search="search" class="elevation-1">
      <template slot="items" slot-scope="props">
        <td class="hover-hand" v-on:click="$router.push({path: '/events/' + props.item.id})">{{ props.item.title }}</td>
        <td class="hover-hand" v-on:click="$router.push({path: '/events/' + props.item.id})">{{ getDisplayDate(props.item.start) }}</td>
        <td class="hover-hand" v-on:click="$router.push({path: '/events/' + props.item.id})">{{ props.item.location_name }}</td>
        <td>
          <!-- <v-icon small @click="editEvent(props.item)">edit</v-icon> -->
          <v-tooltip bottom>
            <v-btn
              icon
              outline
              small
              color="primary"
              slot="activator"
              v-on:click="editEvent(props.item)"
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
              v-on:click="confirmDeactivate(props.item)"
            >
              <v-icon small>delete</v-icon>
            </v-btn>
            <span>{{ $t("actions.tooltips.deactivate") }}</span>
          </v-tooltip>
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
    <v-dialog v-model="eventDialog.show" max-width="500px">
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

    <!-- Deactivate dialog -->
    <v-dialog v-model="deactivateDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{ $t("events.confirm-deactivate") }}</v-card-text>
          <v-card-actions>
            <v-btn v-on:click="cancelDeactivate" color="secondary" flat data-cy="">{{ $t("actions.cancel") }}</v-btn>
            <v-spacer></v-spacer>
            <v-btn v-on:click="deactivateEvent" color="primary" raised :loading="deactivateDialog.loading" data-cy="">{{ $t("actions.confirm") }}</v-btn>
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
    this.$http.get("http://localhost:3000/events").then(resp => {
      this.events = resp.data;
    });
  },

  data() {
    return {
      events: [],
      eventDialog: {
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        event: {}
      },
      deactivateDialog: {
        show: false,
        eventId: -1,
        loading: false
      },
      search: "",

      snackbar: {
        show: false,
        text: ""
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

    activateDeactivateDialog(eventId) {
      this.deactivateDialog.show = true;
      this.deactivateDialog.eventId = eventId;
    },

    confirmDeactivate(event) {
      this.activateDeactivateDialog(event.id);
    },
    
    deactivateEvent() {
      console.log("deactivated event")
      this.deactivateDialog.loading = true;
      const eventId = this.deactivateDialog.eventId
      const idx = this.events.findIndex(ev => ev.id === eventId);
      this.$http
        .delete(`http://localhost:3000/events/${eventId}`)
        .then(resp => {
          console.log("DELETED", resp);
          this.events.splice(idx, 1);
          this.deactivateDialog.loading = false;
          this.deactivateDialog.show = false;
          this.showSnackbar(this.$t("events.event-deleted"));
        })
        .catch(err => {
          console.error("DELETE FALURE", err.response);
          this.deactivateDialog.loading = false;
          this.showSnackbar(this.$t("events.error-deleting-event"));
        });

      // this.deactivateDialog.show = false;
    },

    cancelDeactivate() {
      this.deactivateDialog.show = false;
    },

    newEvent() {
      this.activateEventDialog();
    },

    cancelEvent() {
      this.eventDialog.show = false;
    },

    saveEvent(event) {
      this.eventDialog.saveLoading = true;
      if (this.eventDialog.editMode) {
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
      } else {
        this.$http
          .post("http://localhost:3000/events/", event)
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
      this.$http
          .post("http://localhost:3000/events/", event)
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
          year:'numeric',
          month:'numeric',
          day:'numeric',
          hour: '2-digit',
          minute:'2-digit'
      });
    }
  }
};
</script>

<style scoped>
.hover-hand {
  cursor: pointer;
}
</style>