<template>
  <div>
    <v-toolbar>
      <v-toolbar-title>Event Table</v-toolbar-title>
      <v-spacer></v-spacer>
      <!-- <v-text-field
        v-model="search"
        append-icon="search"
        v-bind:label="$t('actions.search')"
        single-line
        hide-details
      ></v-text-field>-->
      <v-spacer></v-spacer>

      <v-btn small fab color="primary" absolute dark bottom right v-on:click.stop="newEvent">
        <v-icon>add</v-icon>
      </v-btn>
    </v-toolbar>

    <v-data-table :headers="headers" :items="events" class="elevation-1">
      <template slot="items" slot-scope="props">
        <td>{{ props.item.title }}</td>
        <td>
          <v-icon small @click="editEvent(props.item)">edit</v-icon>
        </td>
      </template>
    </v-data-table>

    <!-- New/Edit dialog -->
    <v-dialog v-model="eventDialog.show" max-width="500px">
      <event-form
        v-bind:editMode="eventDialog.editMode"
        v-bind:initialData="eventDialog.event"
        v-on:cancel="cancelEvent"
        v-on:save="saveEvent"
      />
    </v-dialog>
  </div>
</template>

<script>
import EventForm from "./EventForm";

export default {
  name: "EventTable",
  components: { "event-form": EventForm },
  data() {
    return {
      events: [{ title: "event1" }, { title: "event2" }, { title: "event3" }],
      eventDialog: {
        show: false,
        editMode: false,
        event: {}
      }
    };
  },
  computed: {
    headers() {
      return [{ text: "Event Title" }, { text: "Actions", sortable: false }];
    }
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

    newEvent() {
      this.activateEventDialog();
    },

    cancelEvent() {
      this.eventDialog.show = false;
    },

    saveEvent(event) {
      console.log(event);
      this.eventDialog.show = false;
    }
  }
};
</script>