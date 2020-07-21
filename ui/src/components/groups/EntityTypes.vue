<template>
  <div>
    <v-btn
      class="mb-3"
      outlined
      color="primary"
      v-on:click="$router.push({ path: '/groups/all' })"
      ><v-icon>arrow_back</v-icon>{{ $t("actions.back") }}</v-btn
    >
    <v-card>
      <v-toolbar :color="toolbarColor" class="pa-1">
        <v-row no-gutters align="center" justify="space-between">
          <v-col v-if="select">
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-btn v-on:click="selected = {}" v-on="on" small fab>
                  <v-icon>close</v-icon>
                </v-btn>
              </template>
              {{ $t("actions.close") }}
            </v-tooltip>
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-btn
                  color="primary"
                  v-on:click="showChangeEntityTypeDialog"
                  v-on="on"
                  small
                  fab
                >
                  <v-icon>low_priority</v-icon>
                </v-btn>
              </template>
              {{ getTranslation("change-to-different") }}
            </v-tooltip>
          </v-col>
          <v-col v-else>
            <v-toolbar-title>{{ getTranslation("title") }}</v-toolbar-title>
          </v-col>
          <v-col md="4">
            <v-text-field
              v-model="search"
              append-icon="search"
              v-bind:label="$t('actions.search')"
            ></v-text-field>
          </v-col>
          <v-col md="4" class="text-xs-right">
            <v-btn
              :disabled="select"
              raised
              :fab="$vuetify.breakpoint.smAndDown"
              :small="$vuetify.breakpoint.smAndDown"
              color="primary"
              @click="showEntityTypeDialog()"
              ><v-icon>add</v-icon>
              {{ $vuetify.breakpoint.smAndDown ? "" : getTranslation("new") }}
            </v-btn>
          </v-col>
        </v-row>
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
            <tr @click="props.expanded = !props.expanded">
              <td><v-icon>category</v-icon> {{ props.item.name }}</td>
              <td>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on }">
                    <v-btn
                      icon
                      outlined
                      small
                      color="primary"
                      v-on:click.stop="showEntityTypeDialog(props.item)"
                      v-on="on"
                    >
                      <v-icon small>edit</v-icon>
                    </v-btn>
                  </template>
                  {{ $t("actions.edit") }}
                </v-tooltip>
                <v-tooltip
                  bottom
                  v-if="
                    (isGroupTypeMode ? props.item.groups : props.item.managers)
                      .length === 0
                  "
                >
                  <template v-slot:activator="{ on }">
                    <v-btn
                      icon
                      outlined
                      small
                      color="primary"
                      v-on:click.stop="
                        showDeleteEntityTypeDialog(props.item.id)
                      "
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
                      outlined
                      small
                      color="primary"
                      v-on:click.stop="props.expanded = !props.expanded"
                      v-on="on"
                    >
                      <v-icon v-if="!props.expanded" small>expand_more</v-icon>
                      <v-icon v-else small>expand_less</v-icon>
                    </v-btn>
                  </template>
                  {{
                    props.expanded
                      ? getTranslation("hide-expand")
                      : getTranslation("show-expand")
                  }}
                </v-tooltip>
              </td>
            </tr>
          </template>
          <template v-slot:expand="{ item }">
            <v-list
              v-if="(isGroupTypeMode ? item.groups : item.managers).length != 0"
              dense
            >
              <v-list-tile
                @click="toggleEntitySelection(entity)"
                v-for="entity in isGroupTypeMode ? item.groups : item.managers"
                :key="entity.id"
              >
                <v-list-tile-action>
                  <v-checkbox :value="entitySelected(entity)"></v-checkbox>
                </v-list-tile-action>
                <v-list-tile-avatar
                  ><v-icon>{{
                    isGroupTypeMode ? "people" : "account_circle"
                  }}</v-icon></v-list-tile-avatar
                >
                <v-list-tile-content> {{ entity.name }} </v-list-tile-content>
              </v-list-tile>
            </v-list>
          </template>
        </v-data-table>
      </v-card-text>

      <!-- change entityType dialog -->
      <v-dialog max-width="350px" v-model="changeEntityTypeDialog.show">
        <v-card>
          <v-card-title>
            <span class="headline">{{
              getTranslation("change-to-different")
            }}</span>
          </v-card-title>
          <v-card-text>
            <v-chip v-for="(value, key) in selected" :key="key">
              <v-icon> people </v-icon>
              {{ value.name }}</v-chip
            >
            <entity-type-form
              :entity-type-name="entityTypeName"
              :key="entityTypeFormKey"
              v-model="changeEntityTypeDialog.entityType"
            ></entity-type-form>
          </v-card-text>
          <v-card-actions>
            <v-btn text @click="hideChangeEntityTypeDialog">{{
              $t("actions.cancel")
            }}</v-btn>
            <v-btn
              color="primary"
              text
              :loading="changeEntityTypeDialog.loading"
              :disabled="isEmpty(changeEntityTypeDialog.entityType)"
              @click="
                changeToEntityType(
                  changeEntityTypeDialog.entityType.id,
                  Object.values(selected)
                ).then(() => (selected = {}))
              "
              >{{ $t("actions.confirm") }}</v-btn
            >
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- add/edit entityType dialog -->
      <v-dialog v-model="entityTypeDialog.show" max-width="350px">
        <v-card>
          <v-card-title>
            <span class="headline">
              {{
                entityTypeDialog.editMode
                  ? getTranslation("edit")
                  : getTranslation("new")
              }}
            </span>
          </v-card-title>
          <v-card-text>
            <v-text-field
              :label="getTranslation('name')"
              v-model="entityTypeDialog.entityType.name"
            ></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-btn text @click="hideEntityTypeDialog">{{
              $t("actions.close")
            }}</v-btn>
            <v-btn
              text
              :disabled="entityTypeDialog.entityType.name === ''"
              :loading="entityTypeDialog.loading"
              color="primary"
              @click="saveEntityType"
              >{{ $t("actions.save") }}</v-btn
            >
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- delete entityType dialog -->
      <v-dialog v-model="deleteEntityTypeDialog.show" max-width="350px">
        <v-card>
          <v-card-text>{{ getTranslation("confirm-remove") }}</v-card-text>
          <v-card-actions>
            <v-btn text color="secondary" @click="hideDeleteEntityTypeDialog">{{
              $t("actions.cancel")
            }}</v-btn>
            <v-btn
              text
              color="primary"
              :loading="deleteEntityTypeDialog.loading"
              @click="deleteEntityType"
              >{{ $t("actions.confirm") }}</v-btn
            >
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card>
  </div>
</template>
<script>
import { eventBus } from "../../plugins/event-bus.js";
import { isEmpty } from "lodash";
import EntityTypeForm from "./EntityTypeForm";
export default {
  name: "EntityTypes",
  components: { EntityTypeForm },
  props: {
    entityTypeName: {
      /* either groupType or managerType */
      type: String,
      default: "groupType",
    },
  },

  computed: {
    isGroupTypeMode() {
      return this.entityTypeName == "groupType";
    },
    endpoint() {
      return `/api/v1/groups/${
        this.isGroupTypeMode ? "group-types" : "manager-types"
      }`;
    },
    headers() {
      if (this.isGroupTypeMode) {
        return [
          {
            text: this.$t("groups.entity-types.group-types.name"),
            value: "name",
          },
          {
            text: this.$t("actions.header"),
            value: "actions",
            sortable: false,
            width: "150px",
          },
        ];
      } else {
        return [
          {
            text: this.$t("groups.entity-types.manager-types.name"),
            value: "name",
          },
          {
            text: this.$t("actions.header"),
            value: "actions",
            sortable: false,
            width: "150px",
          },
        ];
      }
    },
    selectedIds() {
      return Object.keys(this.selected);
    },
    select() {
      return this.selectedIds.length != 0;
    },
    toolbarColor() {
      return this.select ? "blue-grey" : undefined;
    },
  },

  data() {
    return {
      search: "",
      tableLoading: false,
      entityTypes: [],
      selected: {},
      entityTypeFormKey: -1,
      changeEntityTypeDialog: {
        loading: false,
        show: false,
        entityType: {},
      },
      deleteEntityTypeDialog: {
        loading: false,
        show: false,
        entityTypeId: null,
      },
      entityTypeDialog: {
        loading: false,
        show: false,
        editMode: false,
        editingEntityTypeId: null,
        entityType: {
          name: "",
        },
      },
    };
  },

  methods: {
    /* utility */
    isEmpty,
    fetchEntityTypes() {
      this.tableLoading = true;
      this.$http.get(this.endpoint).then((resp) => {
        this.tableLoading = false;
        this.entityTypes = resp.data;
        this.entityTypes.forEach((entityType) => {
          let entityName = this.isGroupTypeMode ? "groups" : "managers";
          this.$set(
            entityType,
            entityName,
            entityType[entityName].filter((entity) => entity.active)
          );
        });
        if (!this.isGroupTypeMode) {
          for (let managerType of this.entityTypes) {
            // for each manager, create a unique pseudo-id and a human-readable name
            managerType.managers.forEach((manager) => {
              manager.id = `g_${manager.group.id}_p_${manager.person.id}`;
              manager.name = `${manager.person.firstName} ${manager.person.lastName} (${manager.group.name})`;
            });
          }
        }
      });
    },
    getTranslation(key) {
      return this.$t(
        `groups.entity-types.${
          this.isGroupTypeMode ? "group-types" : "manager-types"
        }.${key}`
      );
    },

    /* dialog related */
    showChangeEntityTypeDialog() {
      this.changeEntityTypeDialog.show = true;
    },
    hideChangeEntityTypeDialog() {
      this.changeEntityTypeDialog.entityType = {};
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
    toggleEntitySelection(entity) {
      if (Object.prototype.hasOwnProperty.call(this.selected, entity.id)) {
        this.$delete(this.selected, entity.id);
      } else {
        this.$set(this.selected, entity.id, entity);
      }
    },
    entitySelected(entity) {
      return Object.prototype.hasOwnProperty.call(this.selected, entity.id);
    },

    /* endpoint related */
    deleteEntityType() {
      this.deleteEntityTypeDialog.loading = true;
      let id = this.deleteEntityTypeDialog.entityTypeId;
      this.$http
        .delete(`${this.endpoint}/${id}`, { noErrorSnackBar: true })
        .then(() => {
          this.entityTypeFormKey = `delete_${id}`; // refresh entity-type-form
          this.deleteEntityTypeDialog.loading = false;
          this.hideDeleteEntityTypeDialog();
          this.entityTypes = this.entityTypes.filter(
            (entityType) => entityType.id != id
          );
          eventBus.$emit("message", {
            content: this.getTranslation("success-remove"),
          });
        })
        .catch((err) => {
          console.error("DELETE ERROR", err);
          this.deleteEntityTypeDialog.loading = false;
          this.hideDeleteEntityTypeDialog();
          eventBus.$emit("error", {
            content: this.getTranslation("fail-remove"),
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
        .then((resp) => {
          this.entityTypeFormKey = `add_${resp.data.id}`; // refresh entity-type-form
          this.fetchEntityTypes();
          eventBus.$emit("message", {
            content: this.getTranslation("success-add"),
          });
        })
        .catch((err) => {
          console.error("POST ERROR", err);
          eventBus.$emit("error", {
            content: this.getTranslation("fail-add"),
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
          this.entityTypeFormKey = `update_${id}_${newName}`; // refresh entity-type-form
          this.fetchEntityTypes();
          eventBus.$emit("message", {
            content: this.getTranslation("success-update"),
          });
        })
        .catch((err) => {
          console.error("PATCH ERROR", err);
          eventBus.$emit("error", {
            content: this.getTranslation("fail-update"),
          });
        })
        .finally(() => {
          this.entityTypeDialog.loading = false;
          this.hideEntityTypeDialog();
        });
    },
    changeToEntityType(newEntityTypeId, entities) {
      this.changeEntityTypeDialog.loading = true;
      let promises = [];
      for (let entity of entities) {
        let endpoint;
        if (this.isGroupTypeMode) {
          endpoint = `/api/v1/groups/groups/${entity.id}`;
        } else {
          endpoint = `/api/v1/groups/groups/${entity.group.id}/managers/${entity.person.id}`;
        }
        let payload = {};
        payload[
          this.isGroupTypeMode ? "groupTypeId" : "managerTypeId"
        ] = newEntityTypeId;
        promises.push(
          this.$http.patch(endpoint, payload, { noErrorSnackBar: true })
        );
      }
      return Promise.all(promises)
        .then(() => {
          this.fetchEntityTypes();
          eventBus.$emit("message", {
            content: this.getTranslation("success-change"),
          });
        })
        .catch(() => {
          eventBus.$emit("error", {
            content: this.getTranslation("fail-change"),
          });
        })
        .finally(() => {
          this.changeEntityTypeDialog.loading = false;
          this.hideChangeEntityTypeDialog();
        });
    },
  },

  mounted() {
    this.fetchEntityTypes();
  },
};
</script>
