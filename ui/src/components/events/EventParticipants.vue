<template>
  <div>
    <v-toolbar>
      <v-toolbar-title>{{ $t("events.participants.title") }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="search"
        v-bind:label="$t('actions.search')"
        single-line
        hide-details
      ></v-text-field>
      <v-spacer></v-spacer>
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
      :rows-per-page-items="rowsPerPageItem"
      :headers="headers"
      :items="people"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td>{{ props.item.person.firstName }}</td>
        <td>{{ props.item.person.lastName }}</td>
        <td>{{ props.item.person.email }}</td>
        <td>{{ props.item.person.phone }}</td>
        <td>
          <v-tooltip bottom>
            <v-btn
              icon
              outline
              small
              color="primary"
              slot="activator"
              v-on:click="confirmDelete(props.item)"
              data-cy="archive"
            >
              <v-icon small>delete</v-icon>
            </v-btn>
            <span>{{ $t("actions.tooltips.remove") }}</span>
          </v-tooltip>
        </td>
      </template>
    </v-data-table>

    <!-- Add Participant Dialog -->
    <v-dialog v-model="addParticipantDialog.show" max-width="350px">
      <v-card>
        <v-card-title primary-title>
          <div>
            <h3 class="headline mb-0">
              {{ $t("person.actions.add-participant") }}
            </h3>
          </div>
        </v-card-title>
        <v-card-text>
          <!-- TODO maybe include existingEntities -->
          <entity-search
            multiple
            person
            v-model="addParticipantDialog.newParticipants"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelNewParticipantDialog"
            color="secondary"
            flat
            data-cy=""
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="addParticipants"
            :disabled="addParticipantDialog.newParticipants.length == 0"
            color="primary"
            raised
            :loading="addParticipantDialog.loading"
            data-cy="confirm-participant"
            >{{ $t("events.participants.add") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete dialog -->
    <v-dialog v-model="deleteDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{
          $t("events.participants.confirm-remove")
        }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelDelete"
            color="secondary"
            flat
            data-cy="cancel-delete"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deleteParticipant"
            color="primary"
            raised
            :loading="deleteDialog.loading"
            data-cy="confirm-delete"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false">
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>
  </div>
</template>

<script>
import EntitySearch from "../EntitySearch";
export default {
  components: { "entity-search": EntitySearch },
  name: "EventParticipants",
  data() {
    return {
      rowsPerPageItem: [
        10,
        15,
        25,
        { text: "$vuetify.dataIterator.rowsPerPageAll", value: -1 }
      ],
      tableLoading: false,
      search: "",
      people: [],
      addParticipantDialog: {
        show: false,
        newParticipants: [],
        loading: false
      },
      deleteDialog: {
        show: false,
        participantId: -1,
        loading: false
      },

      snackbar: {
        show: false,
        text: ""
      }
    };
  },

  computed: {
    headers() {
      return [
        {
          text: this.$t("person.name.first"),
          value: "person.firstName",
          width: "20%"
        },
        {
          text: this.$t("person.name.last"),
          value: "person.lastName",
          width: "20%"
        },
        {
          text: this.$t("person.email"),
          value: "person.email",
          width: "22.5%"
        },
        {
          text: this.$t("person.phone"),
          value: "person.phone",
          width: "22.5%"
        },
        { text: this.$t("actions.header"), sortable: false }
      ];
    }
  },

  methods: {
    activateNewParticipantDialog() {
      this.addParticipantDialog.show = true;
    },
    openParticipantDialog() {
      this.activateNewParticipantDialog();
    },
    cancelNewParticipantDialog() {
      this.addParticipantDialog.show = false;
    },

    addParticipants() {
      this.addParticipantDialog.loading = true;
      let promises = [];

      for (let person of this.addParticipantDialog.newParticipants) {
        const idx = this.people.findIndex(
          ev_pe => ev_pe.person_id === person.id
        );
        if (idx === -1) {
          promises.push(this.addParticipant(person.id));
        }
      }

      Promise.all(promises)
        .then(() => {
          this.showSnackbar(this.$t("events.participants.added"));
          this.addParticipantDialog.loading = false;
          this.addParticipantDialog.show = false;
          this.addParticipantDialog.newParticipants = [];
          this.getParticipants();
        })
        .catch(err => {
          console.log(err);
          this.addParticipantDialog.loading = false;
          this.showSnackbar(this.$t("events.participants.error-adding"));
        });
    },

    addParticipant(id) {
      const eventId = this.$route.params.event;
      return this.$http.post(`/api/v1/events/${eventId}/participants/${id}`, {
        confirmed: true
      });
    },

    confirmDelete(event) {
      this.activateDeleteDialog(event.person_id);
    },

    deleteParticipant() {
      this.deleteDialog.loading = true;
      const participantId = this.deleteDialog.participantId;
      const idx = this.people.findIndex(ev => ev.person.id === participantId);
      const id = this.$route.params.event;
      this.$http
        .delete(`/api/v1/events/${id}/participants/${participantId}`)
        .then(() => {
          this.deleteDialog.loading = false;
          this.deleteDialog.show = false;
          this.people.splice(idx, 1);
          this.showSnackbar(this.$t("events.participants.removed"));
        })
        .catch(err => {
          console.log(err);
          this.deleteDialog.loading = false;
          this.deleteDialog.show = false;
          this.showSnackbar(this.$t("events.participants.error-removing"));
        });
    },
    cancelDelete() {
      this.deleteDialog.show = false;
    },
    activateDeleteDialog(participantId) {
      this.deleteDialog.show = true;
      this.deleteDialog.participantId = participantId;
    },
    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },

    getParticipants() {
      this.tableLoading = true;
      const id = this.$route.params.event;
      this.$http
        .get(`/api/v1/events/${id}?include_participants=1`)
        .then(resp => {
          let event = resp.data;
          this.people = event.participants;
          this.tableLoading = false;
        });
    }
  },

  mounted: function() {
    this.getParticipants();
  }
};
</script>
