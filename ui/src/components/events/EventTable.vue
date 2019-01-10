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

      <v-btn small fab color="primary" absolute dark bottom right v-on:click.stop="newEvent">
        <v-icon>add</v-icon>
      </v-btn>
    </v-toolbar>

    <v-data-table :headers="headers" :items="events" :search="search" class="elevation-1">
      <template slot="items" slot-scope="props">
        <td>{{ props.item.title }}</td>
        <td>{{ getDisplayDate(props.item.start) }}</td>
        <td>{{ props.item.location_name }}</td>
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
              v-on:click="deleteEvent(props.item)"
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
      />
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

    deleteEvent(event) {
      console.log('delete!')
    },

    newEvent() {
      this.activateEventDialog();
    },

    cancelEvent() {
      this.eventDialog.show = false;
    },

    saveEvent(event) {
      console.log(event);
      if (this.eventDialog.editMode) {
        this.$http.put('http://localhost:3000/events', event).then(res => {
          this.snackbar.show = true;
          this.snackbar.text = 'saved?'
        })
      } else {
        this.$http.post('http://localhost:3000/events', event).then(res => {
          this.snackbar.show = true;
          this.snackbar.text = 'posted?'
        })
      }
      this.eventDialog.show = false;
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