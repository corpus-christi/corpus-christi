<template>
    <div>
        <v-toolbar>
            <v-toolbar-title>{{ $t('events.participants.title') }}</v-toolbar-title>
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
        v-on:click="openParticipantDialog"
        data-cy="add-participant"
      >
        <v-icon dark left>add</v-icon>
        {{ $t("actions.add-person") }}
      </v-btn>
    </v-toolbar>
    <v-data-table
      :headers="headers"
      :items="people"
      :search="search"
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td>{{ props.item.firstName }}</td>
        <td>{{ props.item.lastName }}</td>
        <td>{{ props.item.email }}</td>
        <td>{{ props.item.phone }}</td>
        <td></td>
      </template>
    </v-data-table>

      <v-dialog v-model="newParticipantDialog.show" max-width="350px">
        <v-card>
            <v-card-title primary-title>
                <div>
                    <h3 class="headline mb-0">{{ $t('person.actions.add-participant') }}</h3>
                </div>
            </v-card-title>
            <v-card-text>
                <entity-search
                person
                v-model="newParticipant"/>
            </v-card-text>
            <v-card-actions>
                <v-btn v-on:click="cancelNewParticipantDialog" color="secondary" flat data-cy="">{{ $t("actions.cancel") }}</v-btn>
                <v-spacer></v-spacer>
                <v-btn v-on:click="addParticipant" :disabled="newParticipant == null" color="primary" raised :loading="newParticipantDialog.loading" data-cy="">Add Participant</v-btn>
            </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
</template>

<script>
import EntitySearch from "../EntitySearch";
export default {
  components: { "entity-search": EntitySearch },
  name: "EventParticipants",
  data() {
    return {
      selectedValue: null,
      search: "",
      people: [],
      newParticipant: null,
      newParticipantDialog: {
        show: false,
        eventId: -1,
        loading: false
      }
    };
  },

  computed: {
    headers() {
      return [
        {
          text: this.$t("person.name.first"),
          value: "firstName",
          width: "20%"
        },
        { text: this.$t("person.name.last"), value: "lastName", width: "20%" },
        { text: this.$t("person.email"), value: "email", width: "22.5%" },
        { text: this.$t("person.phone"), value: "phone", width: "22.5%" },
        { text: this.$t("actions.header"), sortable: false }
      ];
    }
  },

  methods: {
    activateNewParticipantDialog(eventId) {
      this.newParticipantDialog.show = true;
      this.newParticipantDialog.eventId = eventId;
    },
    openParticipantDialog(event) {
      this.activateNewParticipantDialog(event.id);
    },
    cancelNewParticipantDialog() {
      this.newParticipantDialog.show = false;
    },
    addParticipant() {
      // loading true
      // axios post
      // success -> re-request participants all
      // loading false
      this.newParticipantDialog.show = false;
      this.newParticipant = null;
    },
    deleteParticipant() {
      // loading true
      // axios post
      // success -> re-request participants all
      // loading false
    }
  },

  mounted: function() {
    this.$http
      .get("/api/v1/people/persons")
      .then(resp => (this.people = resp.data));
  }
};
</script>
