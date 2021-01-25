<template>
  <div>
    <v-card elevation=8>
      <template v-if="loaded"> 
        <v-toolbar elevation=0 rounded>
          <v-toolbar-title v-if="item == 'team'">{{ $t("teams.title") }}</v-toolbar-title>
          <v-toolbar-title v-else-if="item == 'person'">{{ $t("events.persons.title") }}</v-toolbar-title>
          <v-toolbar-title v-else>{{ $t("groups.title") }}</v-toolbar-title>
          <v-spacer/>
          <v-btn
            v-if="item === 'team'"
            right
            text
            color="primary"
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
            color="primary"
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
            color="primary"
            data-cy="add-group-dialog"
            @click="showAddItemDialog"
          >
            <v-icon left>add</v-icon>
            {{ $t("groups.new") }}
          </v-btn>
        </v-toolbar>
        <v-list v-if="items.length">
          <template v-for="(jItem) in items">
            <v-divider v-bind:key="`${item}Divider` + jItem.id"></v-divider>
            <v-list-item v-bind:key="jItem.id">
              <v-list-item-content>
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
                >
                  <v-icon>info</v-icon>
                </v-btn>
              </v-list-item-action>
              <v-list-item-action class="ml-1 mr-1">
                <v-btn
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
          </template>
        </v-list>
      </template>
    </v-card>

    <!-- Add Item Dialog -->
    <v-dialog v-model="addItemDialog.show" persistent max-width="500px">
        <v-card>
          <v-card-title v-if="item === 'team'" primary-title>
            <span class="headline">{{ $t("teams.new") }}</span>
          </v-card-title>
          <v-card-title v-else-if="item === 'person'" primary-title>
            <span class="headline">{{ addPersonDialogTitle }}></span>
          </v-card-title>
          <v-card-title v-else-if="item === 'group'">
            <span class="headline">{{ $t("actions.add-group") }}</span>
          </v-card-title>

          <v-card-text>
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
  </div>
</template>

<script>
import EntitySearch from '../EntitySearch.vue';

export default {
  name: "EventItemDetails",
  components: {
    // eslint-disable-next-line vue/no-unused-components
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
      },

      deleteItemDialog: {
        show: false,
        loading: false,
        itemId: -1,
      }
    }
  },

  computed: {
    addPersonDialogTitle() {
      return this.addPersonDialog.editMode
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
    },

    addItem() {
      // Emit item-added event
      this.addItemDialog.loading = true;
      this.$emit("item-added", { item: this.addItemDialog.newItem });
      this.closeAddItemDialog();
    }

    

  },

};
</script>
