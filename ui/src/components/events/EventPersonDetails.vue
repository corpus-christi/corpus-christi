<template>
  <div>
    <v-card class="ma-1">
      <template v-if="loaded">
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
              <v-list-tile-content>
                <v-container fluid class="pa-0">
                  <v-layout align-center row justify-space-between>
                    <v-flex>
                      {{ getFullName(person.person) }}
                      <template v-if="person.description">
                        - {{ person.description }}</template
                      >
                    </v-flex>
                    <v-flex shrink>
                      <v-layout>
                        <v-flex xs6>
                          <v-btn
                            icon
                            outline
                            flat
                            color="primary"
                            v-on:click="openEditDialog(person)"
                            :data-cy="'editPerson-' + person.id"
                            ><v-icon>edit</v-icon>
                          </v-btn>
                        </v-flex>
                        <v-flex xs6>
                          <v-btn
                            icon
                            outline
                            flat
                            color="primary"
                            v-on:click="showDeletePersonDialog(person.id)"
                            :data-cy="'deletePerson-' + person.id"
                            ><v-icon>delete</v-icon>
                          </v-btn>
                        </v-flex>
                      </v-layout>
                    </v-flex>
                  </v-layout>
                </v-container>
              </v-list-tile-content>
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
          <span class="headline">{{ addPersonDialogTitle }}</span>
        </v-card-title>
        <v-card-text>
          <v-text-field
            readonly
            disabled
            v-if="addPersonDialog.editMode"
            v-bind:value="getFullName(addPersonDialog.person)"
          ></v-text-field>
          <!-- TODO conditionally hide, don't remove -->
          <div :hidden="addPersonDialog.editMode">
            <entity-search
              person
              data-cy="person-entity-search"
              v-model="addPersonDialog.person"
              :existing-entities="persons"
            ></entity-search>
          </div>
          <v-textarea
            rows="1"
            v-model="addPersonDialog.description"
            v-bind:label="$t('events.persons.description')"
            name="description"
            data-cy="description"
          ></v-textarea>
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
    loaded: {
      type: Boolean,
      required: true
    }
  },

  data() {
    return {
      addPersonDialog: {
        editMode: false,
        show: false,
        loading: false,
        person: null,
        description: ""
      },

      deletePersonDialog: {
        show: false,
        loading: false,
        personId: -1
      }
    };
  },
  computed: {
    addPersonDialogTitle() {
      return this.addPersonDialog.editMode
        ? this.$t("events.persons.edit")
        : this.$t("events.persons.new");
    }
  },

  methods: {
    closeAddPersonDialog() {
      this.addPersonDialog.loading = false;
      this.addPersonDialog.show = false;
      this.addPersonDialog.editMode = false;
      this.addPersonDialog.person = null;
      this.addPersonDialog.description = "";
    },

    openEditDialog(eventPerson) {
      this.addPersonDialog.editMode = true;
      this.addPersonDialog.show = true;
      this.$set(this.addPersonDialog, "person", eventPerson.person);
      this.addPersonDialog.description = eventPerson.description;
    },

    addPerson() {
      const eventId = this.$route.params.event;
      let personId = this.addPersonDialog.person.id;
      this.addPersonDialog.loading = true;
      if (!this.addPersonDialog.editMode) {
        const idx = this.persons.findIndex(p => p.id === personId);
        if (idx > -1) {
          this.closeAddPersonDialog();
          this.showSnackbar(this.$t("events.persons.person-on-event"));
          return;
        }
      }
      let body = { description: this.addPersonDialog.description };
      let promise;
      if (this.addPersonDialog.editMode) {
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
          if (this.addPersonDialog.editMode) {
            this.showSnackbar(this.$t("events.persons.person-edited"));
          } else {
            this.showSnackbar(this.$t("events.persons.person-added"));
          }
          this.$emit("person-added");
          this.closeAddPersonDialog();
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
    },

    getFullName(person) {
      return `${person.firstName} ${person.lastName}`;
    }
  }
};
</script>
