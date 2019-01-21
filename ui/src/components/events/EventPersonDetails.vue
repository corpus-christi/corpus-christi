<template>
  <div>
    <v-card class="ma-1">
      <template v-if="pageLoaded">
        <v-container fill-height fluid>
          <v-flex xs9 sm9 align-end flexbox>
            <span class="headline">{{ $t("events.persons.title") }}</span>
          </v-flex>
          <v-layout xs3 sm3 align-end justify-end>
            <v-btn
              flat
              color="primary"
              data-cy="add-person-dialog"
              v-on:click="addPersonDialog.show = true"
            >
              <v-icon>add</v-icon>&nbsp;{{ $t("events.persons.new") }}
            </v-btn>
          </v-layout>
        </v-container>
        <v-list v-if="persons.length">
          <template v-for="person in persons">
            <v-divider v-bind:key="'personDivider' + person.id"></v-divider>
            <v-list-tile v-bind:key="person.id">
              <v-list-tile-content class="pr-0">
                {{ person.description }}
              </v-list-tile-content>
              <v-list-tile-action>
                <v-btn
                  icon
                  flat
                  color="primary"
                  v-on:click="showDeletePersonDialog(person.id)"
                  :data-cy="'deletePerson-' + person.id"
                  ><v-icon>delete</v-icon>
                </v-btn>
              </v-list-tile-action>
            </v-list-tile>
          </template>
        </v-list>
        <div v-else class="text-xs-center pa-4">
          {{ $t("events.persons.none-assigned") }}
        </div>
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
    <!-- Add Person dialog -->
    <v-dialog v-model="addPersonDialog.show" persistent max-width="500px">
      <v-card>
        <v-card-title primary-title>
          <span class="headline">{{ $t("events.persons.new") }}</span>
        </v-card-title>
        <v-card-text>
          <entity-search
            data-cy="person-entity-search"
            v-model="addPersonDialog.person"
            :existing-entities="persons"
            person
          ></entity-search>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="closeAddPersonDialog()"
            color="secondary"
            flat
            :disabled="addPersonDialog.loading"
            data-cy="cancel-add"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="addPerson()"
            color="primary"
            raised
            :disabled="!addPersonDialog.person"
            :loading="addPersonDialog.loading"
            data-cy="confirm-add"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- Delete Person dialog -->
    <v-dialog v-model="deletePersonDialog.show" max-width="350px">
      <v-card>
        <v-card-text>
          <span>{{ $t("events.persons.confirm-remove-from-event") }}</span>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="deletePersonDialog.show = false"
            color="secondary"
            flat
            :disabled="deletePersonDialog.loading"
            data-cy="cancel-delete"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deletePerson()"
            color="primary"
            raised
            :loading="deletePersonDialog.loading"
            data-cy="confirm-delete"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>
<script>
import EntitySearch from "../EntitySearch";

export default {
  name: "EventPersonDetails",
  components: {
    "entity-search": EntitySearch
  },

  props: {
    persons: {
      required: true
    },
    pageLoaded: {
      type: Boolean,
      required: true
    }
  },

  data() {
    return {
      addPersonDialog: {
        show: false,
        loading: false,
        person: null
      },

      deletePersonDialog: {
        show: false,
        loading: false,
        personId: -1
      }
    };
  },

  methods: {
    closeAddPersonDialog() {
      this.addPersonDialog.loading = false;
      this.addPersonDialog.show = false;
      this.addPersonDialog.person = null;
    },

    addPerson() {
      const eventId = this.$route.params.event;
      let personId = this.addPersonDialog.person.id;
      const idx = this.persons.findIndex(p => p.id === personId);
      this.addPersonDialog.loading = true;
      if (idx > -1) {
        this.closeAddPersonDialog();
        this.showSnackbar(this.$t("events.persons.person-on-event"));
        return;
      }

      this.$http
        .post(`/api/v1/events/${eventId}/individuals/${personId}`)
        .then(() => {
          this.showSnackbar(this.$t("events.persons.person-added"));
          this.closeAddPersonDialog();
          this.$emit("person-added");
        })
        .catch(err => {
          console.log(err);
          this.addPersonDialog.loading = false;
          if (err.response.status == 422) {
            this.showSnackbar(this.$t("events.persons.error-person-assigned"));
          } else {
            this.showSnackbar(this.$t("events.persons.error-adding-person"));
          }
        });
    },

    deletePerson() {
      let id = this.deletePersonDialog.personId;
      const idx = this.persons.findIndex(p => p.id === id);
      this.deletePersonDialog.loading = true;
      const eventId = this.$route.params.event;
      this.$http
        .delete(`/api/v1/events/${eventId}/individuals/${id}`)
        .then(resp => {
          console.log("REMOVED", resp);
          this.deletePersonDialog.show = false;
          this.deletePersonDialog.loading = false;
          this.deletePersonDialog.personId = -1;
          this.persons.splice(idx, 1); //TODO maybe fix me?
          this.showSnackbar(this.$t("events.persons.person-removed"));
        })
        .catch(err => {
          console.log(err);
          this.deletePersonDialog.loading = false;
          this.showSnackbar(this.$t("events.persons.error-removing-person"));
        });
    },

    showDeletePersonDialog(personId) {
      this.deletePersonDialog.personId = personId;
      this.deletePersonDialog.show = true;
    },

    showSnackbar(message) {
      this.$emit("snackbar", message);
    }
  }
};
</script>
