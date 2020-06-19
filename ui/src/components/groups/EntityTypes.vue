<template>
  <v-card>
    <v-toolbar class="pa-1">
      {{ selected }}
      <v-btn @click="showChangeEntityTypeDialog">Change Group Types</v-btn>
      <v-layout align-center justify-space-around>
        <v-flex> <v-toolbar-title>Group Types</v-toolbar-title> </v-flex>
        <v-flex>
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="$t('actions.search')"
          ></v-text-field>
        </v-flex>
        <v-flex justify-content-end>
          <div class="text-xs-center">
            <v-btn
              raised
              :fab="$vuetify.breakpoint.smAndDown"
              :small="$vuetify.breakpoint.smAndDown"
              color="primary"
              @click="showEntityTypeDialog()"
              ><v-icon>add</v-icon>
              {{ $vuetify.breakpoint.smAndDown ? "" : "New Group Type" }}
            </v-btn>
          </div>
        </v-flex>
      </v-layout>
    </v-toolbar>
    <v-card-text>
      <v-data-table
        expand
        :loading="tableLoading"
        :search="search"
        :items="entityTypes"
        :headers="headers"
      >
        <template v-slot:items="props">
          <td>{{ props.item.name }}</td>
          <td>
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-btn
                  icon
                  outline
                  small
                  color="primary"
                  v-on:click="showEntityTypeDialog(props.item)"
                  v-on="on"
                >
                  <v-icon small>edit</v-icon>
                </v-btn>
              </template>
              {{ $t("actions.edit") }}
            </v-tooltip>
            <v-tooltip bottom v-if="props.item.groups.length == 0">
              <template v-slot:activator="{ on }">
                <v-btn
                  icon
                  outline
                  small
                  color="primary"
                  v-on:click="showDeleteEntityTypeDialog(props.item.id)"
                  v-on="on"
                >
                  <v-icon small>delete</v-icon>
                </v-btn>
              </template>
              {{ $t("actions.tooltips.remove") }}
            </v-tooltip>
            <v-tooltip bottom v-else>
              <template v-slot:activator="{ on }">
                <v-btn
                  icon
                  outline
                  small
                  color="primary"
                  v-on:click="props.expanded = !props.expanded"
                  v-on="on"
                >
                  <v-icon v-if="!props.expanded" small>expand_more</v-icon>
                  <v-icon v-else small>expand_less</v-icon>
                </v-btn>
              </template>
              {{ props.expanded ? "Hide groups" : "Show groups" }}
            </v-tooltip>
          </td>
        </template>
        <template v-slot:expand="{ item }">
          <v-list dense>
            <v-list-tile avatar v-for="group in item.groups" :key="group.id">
              <v-list-tile-avatar><v-icon>people</v-icon></v-list-tile-avatar>
              <v-list-tile-content> {{ group.name }} </v-list-tile-content>
              <v-list-tile-action>
                <v-checkbox :value="group.id" v-model="selected"></v-checkbox
              ></v-list-tile-action>
            </v-list-tile>
          </v-list>
        </template>
      </v-data-table>
    </v-card-text>

    <!-- change entityType dialog -->
    <v-dialog max-width="350px" v-model="changeEntityTypeDialog.show">
      <v-card> <entity-type-form></entity-type-form> </v-card>
    </v-dialog>

    <!-- add/edit entityType dialog -->
    <v-dialog v-model="entityTypeDialog.show" max-width="350px">
      <v-card>
        <v-card-title>
          <span class="headline">
            {{
              entityTypeDialog.editMode ? "Edit Group Type" : "New Group Type"
            }}
          </span>
        </v-card-title>
        <v-card-text>
          <v-text-field
            label="Group Type Name"
            v-model="entityTypeDialog.entityType.name"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-btn flat @click="hideEntityTypeDialog">Close</v-btn>
          <v-btn flat color="primary" @click="saveEntityType">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- delete entityType dialog -->
    <v-dialog v-model="deleteEntityTypeDialog.show" max-width="350px">
      <v-card>
        <v-card-text
          >Are you sure you want to delete this group type?</v-card-text
        >
        <v-card-actions>
          <v-btn
            flat
            color="primary"
            :loading="deleteEntityTypeDialog.loading"
            @click="deleteEntityType"
            >{{ $t("actions.confirm") }}</v-btn
          >
          <v-spacer />
          <v-btn flat color="secondary" @click="hideDeleteEntityTypeDialog">{{
            $t("actions.cancel")
          }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>
<script>
import { eventBus } from "../../plugins/event-bus.js";
// import { union } from "lodash";
import EntityTypeForm from "./EntityTypeForm";
export default {
  name: "EntityTypes",
  components: { EntityTypeForm },
  props: {
    entityTypeName: {
      /* either groupType or managerType */
      type: String,
      default: "groupType"
    }
  },
  computed: {
    isGroupTypeMode() {
      return this.entityTypeName == "groupType";
    },
    // allEntities() {
    //   return union(...this.entityTypes.map(et => et[this.isGroupTypeMode?"groups":"managers"]))
    // },
    // selectedEntities() {
    //   return this.
    // },
    endpoint() {
      return `/api/v1/groups/${
        this.isGroupTypeMode ? "group-types" : "manager-types"
      }`;
    },
    headers() {
      if (this.isGroupTypeMode) {
        return [
          { text: "Group Type Name", value: "name" },
          { text: "Actions", value: "actions", sortable: false, width: "10%" }
        ];
      } else {
        return [{ text: "Name", value: "name" }];
      }
    }
  },
  data() {
    return {
      search: "",
      tableLoading: false,
      entityTypes: [],
      selected: [],
      changeEntityTypeDialog: {
        loading: false,
        show: false
      },
      deleteEntityTypeDialog: {
        loading: false,
        show: false,
        entityTypeId: null
      },
      entityTypeDialog: {
        loading: false,
        show: false,
        editMode: false,
        editingEntityTypeId: null,
        entityType: {
          name: ""
        }
      }
    };
  },
  methods: {
    fetchEntityTypes() {
      this.tableLoading = true;
      this.$http.get(this.endpoint).then(resp => {
        this.tableLoading = false;
        console.log(resp.data);
        this.entityTypes = resp.data;
      });
    },
    showChangeEntityTypeDialog() {
      this.changeEntityTypeDialog.show = true;
    },
    hideChangeEntityTypeDialog() {
      this.changeEntityTypeDialog.show = false;
    },
    showDeleteEntityTypeDialog(id) {
      this.deleteEntityTypeDialog.entityTypeId = id;
      this.deleteEntityTypeDialog.show = true;
    },
    hideDeleteEntityTypeDialog() {
      this.deleteEntityTypeDialog.show = false;
    },
    showEntityTypeDialog(entityType = null) {
      if (entityType) {
        this.entityTypeDialog.editMode = true;
        this.entityTypeDialog.editingEntityTypeId = entityType.id;
        this.entityTypeDialog.entityType.name = entityType.name;
      } else {
        this.entityTypeDialog.editMode = false;
        this.entityTypeDialog.entityType.name = "";
      }
      this.entityTypeDialog.show = true;
    },
    hideEntityTypeDialog() {
      this.entityTypeDialog.show = false;
    },
    deleteEntityType() {
      this.deleteEntityTypeDialog.loading = true;
      let id = this.deleteEntityTypeDialog.entityTypeId;
      this.$http
        .delete(`${this.endpoint}/${id}`, { noErrorSnackBar: true })
        .then(() => {
          this.deleteEntityTypeDialog.loading = false;
          this.hideDeleteEntityTypeDialog();
          this.entityTypes = this.entityTypes.filter(
            entityType => entityType.id != id
          );
          eventBus.$emit("message", {
            content: "Successfully removed group type"
          });
        })
        .catch(err => {
          this.deleteEntityTypeDialog.loading = false;
          this.hideDeleteEntityTypeDialog();
          eventBus.$emit("error", {
            content: "Failed to remove the group type"
          });
        });
    },
    saveEntityType() {
      if (this.entityTypeDialog.editMode) {
        this.updateEntityType(
          this.entityTypeDialog.editingEntityTypeId,
          this.entityTypeDialog.entityType.name
        );
      } else {
        this.addEntityType(this.entityTypeDialog.entityType.name);
      }
    },
    addEntityType(newName) {
      this.entityTypeDialog.loading = true;
      this.$http
        .post(this.endpoint, { name: newName }, { noErrorSnackBar: true })
        .then(() => {
          this.fetchEntityTypes();
          eventBus.$emit("message", {
            content: "Successfully added group type name"
          });
        })
        .catch(err => {
          eventBus.$emit("error", {
            content: "Failed to add group type name"
          });
        })
        .finally(() => {
          this.entityTypeDialog.loading = false;
          this.hideEntityTypeDialog();
        });
    },
    updateEntityType(id, newName) {
      this.entityTypeDialog.loading = true;
      this.$http
        .patch(
          `${this.endpoint}/${id}`,
          { name: newName },
          { noErrorSnackBar: true }
        )
        .then(() => {
          this.fetchEntityTypes();
          eventBus.$emit("message", {
            content: "Successfully updated group type name"
          });
        })
        .catch(err => {
          eventBus.$emit("error", {
            content: "Failed to update group type name"
          });
        })
        .finally(() => {
          this.entityTypeDialog.loading = false;
          this.hideEntityTypeDialog();
        });
    },
    changeToEntityType(newEntityTypeId, entityIds) {
      let promises = [];
      for (let entityId of entityIds) {
        let endpoint = `/api/v1/groups/${
          this.isGroupTypeMode ? "groups" : "managers"
        }/${entityId}`;
        let payload = {};
        payload[
          this.isGroupTypeMode ? "groupTypeId" : "managerTypeId"
        ] = newEntityTypeId;
        promises.push(this.$http.patch(endpoint, payload));
      }
      Promise.all(promises).then(() => {
        eventBus.$emit("message", {
          content: "succesfully changed group types"
        });
      });
    }
  },
  mounted() {
    this.fetchEntityTypes();
  }
};
</script>
