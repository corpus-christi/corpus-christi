<template>
  <div>
    <v-card>
      <template v-if="loaded"> 
        <v-toolbar dark color="primary">
          <v-toolbar-title v-if="item == 'team'">{{ $t("teams.title") }}</v-toolbar-title>
          <v-toolbar-title v-else-if="item == 'person'">{{ $t("events.persons.title") }}</v-toolbar-title>
          <v-toolbar-title v-else>{{ $t("groups.title") }}</v-toolbar-title>
          <v-spacer/>
          <v-btn
            v-if="item === 'team'"
            right
            text
            outlined
            data-cy="add-team-dialog"
            @click="showAddItemDialog"
          >
            <v-icon left>add</v-icon>
            {{ $t("teams.new") }}
          </v-btn>
          <v-btn
            v-else-if="item === 'person'"
            right
            text
            outlined
            data-cy="add-person-dialog"
            @click="showAddItemDialog"
          >
            <v-icon left>add</v-icon>
            {{ $t("events.persons.new") }}
          </v-btn>
          <v-btn
            v-else-if="item === 'group'"
            right
            text
            outlined
            data-cy="add-group-dialog"
            @click="showAddItemDialog"
          >
            <v-icon left>add</v-icon>
            {{ $t("actions.add-group") }}
          </v-btn>
        </v-toolbar>
        <v-list v-if="items.length">
          <template v-for="(jItem, index) in items">
            <v-list-item v-bind:key="jItem.id">
              <v-list-item-content v-if="item === 'person'">
                <span>{{ getFullName(jItem.person) }}
                  <template v-if="jItem.description">
                     - {{ jItem.description }}
                    </template>
                </span>
              </v-list-item-content>
              <v-list-item-content v-else>
                <span>{{ jItem.description }}</span>
              </v-list-item-content>
              <v-list-item-action
                v-if="item == 'person'"
                class="ml-1 mr-1"
              >
                <v-btn
                  icon
                  outlined
                  text
                  color="primary"
                  @click="openEditDialog(jItem)"
                >
                  <v-icon>edit</v-icon>
                </v-btn>
              </v-list-item-action>
              <v-list-item-action 
                v-if="item == 'team' || item == 'group'"
                class="ml-1 mr-1"
              >
                <v-btn
                  icon
                  outlined
                  text
                  color="primary"
                  :to="{ path: `/${item}s/${jItem.id}` }"
                >
                  <v-icon>info</v-icon>
                </v-btn>
              </v-list-item-action>
              <v-list-item-action class="ml-1 mr-1">
                <v-btn
                  @click="showDeleteItemDialog(jItem.id)"
                  icon
                  outlined
                  text
                  left
                  color="primary"
                >
                  <v-icon>delete</v-icon>
                </v-btn>
              </v-list-item-action>
            </v-list-item>
            <v-divider v-if="index < items.length - 1" :key="`${item}Divider` + jItem.id"></v-divider>
          </template>
        </v-list>
      </template>
    </v-card>

    <person-dialog
      @snack="showSnackbar"
      @cancel="cancelPerson"
      @attachPerson="attachNewPerson"
      :dialog-state="newPersonDialogState"
      :all-people="allPeople"
      :person="person"
    />

    <!-- Add Item Dialog -->
    <v-dialog v-model="addItemDialog.show" persistent max-width="500px">
        <v-card>
          <v-card-title v-if="item === 'team'" primary-title>
            <span class="headline">{{ $t("teams.new") }}</span>
          </v-card-title>
          <v-card-title v-else-if="item === 'person'" primary-title>
            <span class="headline">{{ addPersonDialogTitle }}</span>
          </v-card-title>
          <v-card-title v-else-if="item === 'group'">
            <span class="headline">{{ $t("actions.add-group") }}</span>
          </v-card-title>

          <v-card-text>
            <v-text-field
              readonly
              disabled
              v-if="item === 'person' && addItemDialog.editMode"
              v-bind:value="getFullName(addItemDialog.newItem)"
            />

            <div :hidden="addItemDialog.editMode">
              <entity-search
                v-if="item === 'team'"
                data-cy="team-entity-search"
                v-model="addItemDialog.newItem"
                :existing-entities="items"
                team
              />
              <entity-search
                v-else-if="item === 'person'"
                data-cy="person-entity-search"
                v-model="addItemDialog.newItem"
                :existing-entities="items"
                person
              />
              <entity-search
                v-else-if="item === 'group'"
                data-cy="group-entity-search"
                v-model="addItemDialog.newItem"
                :existing-entities="items"
                group
              />
              <v-btn
                v-if="item === 'person'"
                color="primary"
                raised
                @click.stop="newPerson"
              >
                <v-icon left>person_add</v-icon>
                {{ $t("actions.add-person") }}
              </v-btn>
            </div>

            <v-textarea
              v-if="item === 'person'"
              rows="1"
              v-model="addItemDialog.description"
              v-bind:label="$t('events.persons.description')"
              name="description"
              data-cy="description"
            />
          </v-card-text>



          <v-card-actions>
            <v-btn
              @click="closeAddItemDialog"
              color="secondary"
              text
              :disabled="addItemDialog.loading"
              data-cy="cancel-add"
            >
              {{ $t("actions.cancel") }}
            </v-btn>
            <v-spacer/>
            <v-btn
              @click="addItem"
              color="primary"
              raised
              :disabled="!addItemDialog.newItem"
              :loading="addItemDialog.loading"
              data-cy="confirm-add"
            >
              {{ $t("actions.confirm") }}
            </v-btn>
          </v-card-actions>
          
        </v-card>
    </v-dialog>

    <!-- Delete Item Dialog -->
    <v-dialog v-model="deleteItemDialog.show" max-width="350px">
      <v-card class="pt-4">
        <v-card-text v-if="item === 'team'">
          <span>{{ $t("teams.confirm-remove-from-event") }}</span>
        </v-card-text>
        <v-card-text v-else-if="item === 'person'">
          <span>{{ $t("events.persons.confirm-remove-from-event") }}</span>
        </v-card-text>
        <v-card-text v-else-if="item === 'group'">
          <span>{{ $t("groups.confirm-remove-from-event") }}</span>
        </v-card-text>

        <v-card-actions>
          <v-btn
            @click="closeDeleteItemDialog"
            color="secondary"
            text
            :disabled="deleteItemDialog.loading"
            data-cy="cancel-delete"
          >
            {{ $t("actions.cancel") }}
          </v-btn>
          <v-spacer/>
          <v-btn
            @click="deleteItem"
            color="primary"
            raised
            :loading="deleteItemDialog.loading"
            data-cy="confirm-delete"
          >
            {{ $t("actions.confirm") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import EntitySearch from '../EntitySearch.vue';
import PersonDialog from "../PersonDialog";

export default {
  name: "EventItemDetails",
  components: {
    // eslint-disable-next-line vue/no-unused-components
    "person-dialog": PersonDialog,
    "entity-search": EntitySearch,
  },

  props: {

   
    item: {
      type: String,
      required: true,
      validator: function (value) {
        return ["team", "person", "group"].indexOf(value) !== -1;
      },
    },

    items: {
      required: true,
    },
    
    loaded: {
      type: Boolean,
      required: true,
    },
  },

  data() {
    return {
      testShow: true,

      addItemDialog: {
        show: false,
        loading: false,
        newItem: null,
        editMode: false,
        description: "",
      },

      deleteItemDialog: {
        show: false,
        loading: false,
        itemId: -1,
      },

      // Attributes needed for creating new people
      newPersonDialogState: "",
      allPeople: [],
      person: {},
    }
  },

  computed: {
    addPersonDialogTitle() {
      return this.addItemDialog.editMode
        ? this.$t("events.persons.edit")
        : this.$t("events.persons.new");
    },
  },

  methods: {
    showAddItemDialog() {
      this.addItemDialog.show = true;
      this.addItemDialog.loading = false;
      this.addItemDialog.newItem = null;
    },

    closeAddItemDialog() {
      this.addItemDialog.show = false;
      this.addItemDialog.loading = false;
      this.addItemDialog.newItem = null;
      this.addItemDialog.editMode = false;
      this.addItemDialog.description = "";
    },

    addItem() {
      this.addItemDialog.loading = true;
      let newData = { item: this.addItemDialog.newItem };
      // If item is a person, add appropriate data
      if (this.item === "person") {
        newData.editMode = this.addItemDialog.editMode;
        newData.description = this.addItemDialog.description;
      }
      // Emit item-added event
      this.$emit("item-added", newData);
      this.closeAddItemDialog();
    },

    showDeleteItemDialog(id) {
      this.deleteItemDialog.itemId = id;
      this.deleteItemDialog.show = true;
    },

    closeDeleteItemDialog() {
      this.deleteItemDialog.show = false;
      this.deleteItemDialog.itemId = -1;
      this.deleteItemDialog.loading = false;
    },

    deleteItem() {
      let id = this.deleteItemDialog.itemId;
      this.deleteItemDialog.loading = true;
      // Emit item-deleted event"
      this.$emit("item-deleted", { itemId: id });
      this.closeDeleteItemDialog();
    },

    openEditDialog(itemData) {
      this.addItemDialog.editMode = true;
      this.addItemDialog.show = true;
      this.$set(this.addItemDialog, "newItem", itemData.person);
      this.addItemDialog.description = itemData.description;
    },

    newPerson() {
      this.newPersonDialogState = "new";
    },

    cancelPerson() {
      this.newPersonDialogState = "";
    },

    attachNewPerson(newPersonData) {
      this.addItemDialog.item = newPersonData;
      this.addItem();
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
