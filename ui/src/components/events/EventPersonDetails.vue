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
              text
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
            <v-list-item v-bind:key="person.id">
              <v-list-item-content>
                <v-container fluid>
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
                            outlined
                            text
                            color="primary"
                            v-on:click="openEditDialog(person)"
                            :data-cy="'editPerson-' + person.id"
                            ><v-icon>edit</v-icon>
                          </v-btn>
                        </v-flex>
                        <v-flex xs6>
                          <v-btn
                            icon
                            outlined
                            text
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
              </v-list-item-content>
            </v-list-item>
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
    <person-dialog
      @snack="showSnackbar"
      @cancel="cancelPerson"
      @attachPerson="attachNewPerson"
      :dialog-state="dialogState"
      :all-people="allPeople"
      :person="person"
    />
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
            <v-btn
              class="mr-0 ml-0"
              color="primary"
              raised
              v-on:click.stop="newPerson"
              data-cy="new-person"
            >
              <v-icon left>person_add</v-icon>
              {{ $t("actions.add-person") }}
            </v-btn>
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
            text
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
            text
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
import PersonDialog from "../PersonDialog";

export default {
  name: "EventPersonDetails",
  components: {
    "entity-search": EntitySearch,
    PersonDialog,
  },

  props: {
    persons: {
      required: true,
    },
    loaded: {
      type: Boolean,
      required: true,
    },
  },

  data() {
    return {
      addPersonDialog: {
        editMode: false,
        show: false,
        loading: false,
        person: null,
        description: "",
      },

      deletePersonDialog: {
        show: false,
        loading: false,
        personId: -1,
      },
      personDialog: {
        show: false,
        title: "",
        person: {},
        addAnotherEnabled: false,
      },
      showingArchived: false,
      selected: [],
      dialogState: "",
      person: {},
      allPeople: [],
      activePeople: [],
      archivedPeople: [],
      search: "",
      data: {},
      translations: {},
    };
  },

  computed: {
    addPersonDialogTitle() {
      return this.addPersonDialog.editMode
        ? this.$t("events.persons.edit")
        : this.$t("events.persons.new");
    },
  },

  methods: {
    newPerson() {
      this.dialogState = "new";
    },

    cancelPerson() {
      this.dialogState = "";
    },

    attachNewPerson(newPersonData) {
      this.addPersonDialog.person = newPersonData;
      this.addPerson();
    },

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
      this.addPersonDialog.loading = true;
      let newData = {
        person: this.addPersonDialog.person,
        editMode: this.addPersonDialog.editMode,
        description: this.addPersonDialog.description,
      };
      // Emit person-added event
      this.$emit("person-added", newData);
      this.closeAddPersonDialog();
    },

    deletePerson() {
      let id = this.deletePersonDialog.personId;
      this.deletePersonDialog.loading = true;
      // Emit person-deleted event
      this.$emit("person-deleted", { personId: id });
      this.deletePersonDialog.show = false;
      this.deletePersonDialog.loading = false;
      this.deletePersonDialog.personId = -1;
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
    },
  },
};
</script>
