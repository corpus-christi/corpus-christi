<template>
  <v-layout>
    <v-flex xs12 sm12>
      <v-card>
        <v-container fill-height fluid>
            <v-flex xs9 sm9 align-end flexbox>
              <span class="headline">Youth Spaghetti Dinner</span>
            </v-flex>
            <v-layout xs3 sm3 align-end justify-end>
              <v-btn flat color="primary" v-on:click="editEvent(event)">
                <v-icon>edit</v-icon>&nbsp;{{ $t('actions.edit') }}
              </v-btn>
            </v-layout>
        </v-container>
        <v-card-text>
          <div>
            <span><b>Location: </b>Coffee Dei</span><br>
            <span><b>Date: </b>1/24/2019</span><br>
            <span><b>Time: </b>6:00 PM - 7:30 PM</span><br><br>  
            <span>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer suscipit id turpis sed hendrerit. 
              In hac habitasse platea dictumst. Aenean ut scelerisque purus. Phasellus a pretium tortor. 
              Nunc et risus eu risus tempus placerat. Pellentesque habitant morbi tristique senectus et netus et 
              malesuada fames ac turpis egestas. Sed pretium imperdiet aliquam. In cursus aliquet mi at gravida. 
              Integer mollis, odio in viverra imperdiet, libero tortor bibendum dui, sit amet congue odio nisl a tortor. 
              Sed suscipit rutrum elit et tincidunt. In egestas sem a sapien pharetra ullamcorper. Maecenas ut sagittis dui. 
              Phasellus vitae tincidunt neque, eu convallis ante. </span><br>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-btn flat color="primary" v-on:click="$router.push({path: '/events/' + $route.params.event + '/participants'})">
            <v-icon>person</v-icon>&nbsp;{{ $t('events.participants.title') }}
          </v-btn>
          <v-btn flat color="primary" v-on:click="$router.push({path: '/events/' + $route.params.event + '/teams'})">
            <v-icon>group</v-icon>&nbsp;{{ $t('events.teams.title') }}
          </v-btn>
          <v-btn flat color="primary" v-on:click="$router.push({path: '/events/' + $route.params.event + '/assets'})">
            <v-icon>devices_other</v-icon>&nbsp;{{ $t('events.assets.title') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-flex>

    <!-- Edit dialog -->
    <v-dialog v-model="eventDialog.show" max-width="500px">
      <event-form
        v-bind:editMode="true"
        v-bind:initialData="eventDialog.event"
        v-bind:saveLoading="eventDialog.saveLoading"
        v-bind:addMoreLoading="eventDialog.addMoreLoading"
        v-on:cancel="cancelEvent"
        v-on:save="saveEvent"
      />
    </v-dialog>
  </v-layout>
</template>

<script>
import EventForm from "./EventForm";

export default {
  name: "EventDetails",
  components: { "event-form": EventForm },
  mounted() {
    this.$http.get("http://localhost:3000/events").then(resp => {
      this.events = resp.data;
    });
  },


  data() {
    return {
      event: {
        "id": 1,
        "title": "Youth Spaghetti Dinner",
        "description": "Come raise support for the youth trip!",
        "start": "2019-01-10T23:00:00.000Z",
        "end": "2019-01-11T02:00:00.000Z",
        "location_name": "Dining Hall",
        "active": true
      },
      eventDialog: {
        event: {},
        show: false,
        saveLoading: false,
      },

      snackbar: {
        show: false,
        text: ""
      }
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
    },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },
  }
}
</script>