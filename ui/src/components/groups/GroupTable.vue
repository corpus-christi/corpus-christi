<template>
  <div>
    <v-toolbar class="pa-1">
      <v-layout align-center justify-space-between fill-height>
        <v-flex md2>
          <v-toolbar-title>{{ $t("groups.header") }}</v-toolbar-title>
        </v-flex>
        <v-flex md2>
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="$t('actions.search')"
            single-line
            hide-details
            data-cy="form-search"
          />
        </v-flex>
        <v-flex md3>
          <v-select
            hide-details
            solo
            single-line
            :items="viewOptions"
            v-model="viewStatus"
            data-cy="view-status-select"
          >
          </v-select>
        </v-flex>
        <v-flex shrink>
          <v-menu open-on-hover offset-y bottom>
            <template v-slot:activator="{ on }">
              <v-btn
                color="primary"
                :fab="$vuetify.breakpoint.mdAndDown"
                :small="$vuetify.breakpoint.mdAndDown"
                v-on="on"
              >
                <v-icon>supervised_user_circle</v-icon>
                {{
                  $vuetify.breakpoint.mdAndDown ? "" : $t("groups.admin-panel")
                }}
              </v-btn>
            </template>
            <v-list>
              <v-list-tile @click.stop="activateGroupDialog()">
                <v-icon color="primary">group_add</v-icon>
                <v-list-tile-content>
                  {{ $t("actions.add-group") }}
                </v-list-tile-content>
              </v-list-tile>
              <v-list-tile :to="{ name: 'group-types' }">
                <v-icon color="primary">view_list</v-icon>
                <v-list-tile-content>
                  {{ $t("groups.entity-types.group-types.manage") }}
                </v-list-tile-content>
              </v-list-tile>
              <v-list-tile :to="{ name: 'manager-types' }">
                <v-icon color="primary">view_list</v-icon>
                <v-list-tile-content>
                  {{ $t("groups.entity-types.manager-types.manage") }}
                </v-list-tile-content>
              </v-list-tile>
            </v-list>
          </v-menu>
        </v-flex>
        <v-flex shrink>
          <v-btn
            color="success"
            :fab="$vuetify.breakpoint.mdAndDown"
            :small="$vuetify.breakpoint.mdAndDown"
            :to="{ name: 'group-treeview' }"
            data-cy="show-treeview"
          >
            <v-icon>account_tree</v-icon>
            {{
              $vuetify.breakpoint.mdAndDown
                ? ""
                : $t("groups.treeview.show-treeview")
            }}
          </v-btn>
        </v-flex>
        <v-flex shrink>
          <v-btn
            color="success"
            :to="{ name: 'group-lineGraph' }"
            data-cy="show-linegraph"
          >
            <v-icon>multiline_chart</v-icon>
            {{
            $t("groups.treeview.show-linegraph")
            }}
          </v-btn>
<!--          //need to be change to En and Spanish-->
        </v-flex>
      </v-layout>
    </v-toolbar>

    <v-data-table
      :headers="headers"
      :rows-per-page-items="rowsPerPageItem"
      :items="visibleGroups"
      :search="search"
      :loading="tableLoading"
      :pagination.sync="paginationInfo"
      must-sort
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td
          class="hover-hand"
          v-on:click="
            $router.push({
              name: 'group-details',
              params: { group: props.item.id }
            })
          "
        >
          {{ props.item.name }}
        </td>
        <td
          class="hover-hand"
          v-on:click="
            $router.push({
              name: 'group-details',
              params: { group: props.item.id }
            })
          "
        >
          {{ props.item.description }}
        </td>
        <td
          class="hover-hand"
          v-on:click="
            $router.push({
              name: 'group-details',
              params: { group: props.item.id }
            })
          "
        >
          {{ props.item.activeMembers.length }}
        </td>
        <td
          class="hover-hand"
          v-on:click="
            $router.push({
              name: 'group-details',
              params: { group: props.item.id }
            })
          "
        >
          {{ props.item.groupType.name }}
        </td>
        <td class="text-no-wrap">
          <template v-if="props.item.active">
            <v-tooltip bottom>
              <v-btn
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="editGroup(props.item)"
                data-cy="edit"
              >
                <v-icon small>edit</v-icon>
              </v-btn>
              <span>{{ $t("actions.edit") }}</span>
            </v-tooltip>
            <v-tooltip bottom>
              <v-btn
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="duplicate(props.item)"
                data-cy="duplicate"
              >
                <v-icon small>filter_none</v-icon>
              </v-btn>
              <span>{{ $t("actions.duplicate") }}</span>
            </v-tooltip>
            <v-tooltip bottom>
              <v-btn
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="showSplitGroupDialog(props.item)"
                data-cy="split"
              >
                <v-icon small>call_split</v-icon>
              </v-btn>
              <span>{{ $t("groups.split.tooltip") }}</span>
            </v-tooltip>
            <v-tooltip bottom>
              <v-btn
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="confirmArchive(props.item)"
                data-cy="archive"
              >
                <v-icon small>archive</v-icon>
              </v-btn>
              <span>{{ $t("actions.tooltips.archive") }}</span>
            </v-tooltip>
          </template>
          <template v-else>
            <v-tooltip bottom v-if="!props.item.active">
              <v-btn
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="unarchive(props.item)"
                :loading="props.item.id < 0"
                data-cy="unarchive"
              >
                <v-icon small>undo</v-icon>
              </v-btn>
              <span>{{ $t("actions.tooltips.activate") }}</span>
            </v-tooltip>
          </template>
        </td>
      </template>
    </v-data-table>

    <!-- New/Edit dialog -->
    <v-dialog v-model="groupDialog.show" max-width="500px" persistent>
      <group-form
        v-bind:editMode="groupDialog.editMode"
        v-bind:initialData="groupDialog.group"
        v-bind:saveLoading="groupDialog.saveLoading"
        v-bind:addMoreLoading="groupDialog.addMoreLoading"
        v-on:cancel="cancelGroup"
        v-on:save="saveGroup"
        v-on:add-another="addAnotherGroup"
      />
    </v-dialog>

    <!-- Archive dialog -->
    <v-dialog v-model="archiveDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{ $t("groups.messages.confirm-archive") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelArchive"
            color="secondary"
            flat
            data-cy="cancel-archive"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer />
          <v-btn
            v-on:click="archiveGroup"
            color="primary"
            raised
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Split Group Dialog -->
    <v-dialog v-model="splitGroupDialog.show" max-width="1300px" persistent>
      <split-group-form
        @cancel="hideSplitGroupDialog"
        @success="handleSplitGroupSuccess"
        @error="hideSplitGroupDialog"
        :initial-data="splitGroupDialog.parentGroup"
      />
    </v-dialog>
  </div>
</template>

<script>
import GroupForm from "./GroupForm";
import SplitGroupForm from "./SplitGroupForm";
import { eventBus } from "../../plugins/event-bus.js";
import { pick } from "lodash";
export default {
  components: { GroupForm, SplitGroupForm },
  name: "GroupTable",
  mounted() {
    this.fetchGroups();
  },
  data() {
    return {
      rowsPerPageItem: [
        10,
        15,
        25,
        { text: "$vuetify.dataIterator.rowsPerPageAll", value: -1 }
      ],
      paginationInfo: {
        sortBy: "activeMembers.length", //default sorted column
        descending: true,
        rowsPerPage: 10,
        page: 1
      },
      tableLoading: true,
      groups: [],

      search: "",
      viewStatus: "viewActive",
      groupDialog: {
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        editingGroupId: null,
        group: {}
      },
      archiveDialog: {
        show: false,
        groupId: -1,
        loading: false
      },
      splitGroupDialog: {
        show: false,
        parentGroup: {}
      }
    };
  },

  computed: {
    viewOptions() {
      return [
        { text: this.$t("actions.view-active"), value: "viewActive" },
        { text: this.$t("actions.view-archived"), value: "viewArchived" },
        { text: this.$t("actions.view-all"), value: "viewAll" }
      ];
    },

    visibleGroups() {
      let list = this.groups;

      if (this.viewStatus === "viewActive") {
        return list.filter(ev => ev.active);
      } else if (this.viewStatus === "viewArchived") {
        return list.filter(ev => !ev.active);
      } else {
        return list;
      }
    },

    headers() {
      return [
        { text: this.$t("groups.name"), value: "name" },
        { text: this.$t("groups.description"), value: "description" },
        { text: this.$t("groups.member-count"), value: "activeMembers.length" },
        { text: this.$t("groups.group-type"), value: "groupType.name" },
        { text: this.$t("actions.header"), sortable: false }
      ];
    }
  },

  methods: {
    fetchGroups() {
      this.tableLoading = true;
      this.$http.get("/api/v1/groups/groups").then(resp => {
        this.groups = resp.data;
        this.groups.forEach(group => {
          group.activeMembers = group.members.filter(member => member.active);
        });
        this.tableLoading = false;
      });
    },
    activateGroupDialog(group = {}, editMode = false) {
      this.groupDialog.editMode = editMode;
      this.groupDialog.group = group;
      this.groupDialog.show = true;
    },
    cancelGroup() {
      this.groupDialog.show = false;
    },

    saveGroup(group, closeDialog = true) {
      this.groupDialog.saveLoading = true;
      let payload = pick(group, ["name", "description"]);
      payload.groupTypeId = group.groupType.id;
      if (this.groupDialog.editMode) {
        this.patchGroup(payload, this.groupDialog.editingGroupId).then(() => {
          let oldGroup = this.groups.find(
            g => g.id === this.groupDialog.editingGroupId
          );
          Object.assign(oldGroup, group);
        });
      } else {
        this.postGroup(payload);
      }
      if (closeDialog) {
        this.closeDialog();
      }
    },

    patchGroup(group, groupId) {
      return this.$http
        .patch(`/api/v1/groups/groups/${groupId}`, group)
        .then(resp => {
          this.groupDialog.saveLoading = false;
          eventBus.$emit("message", {
            content: this.$t("groups.messages.group-edited")
          });
        })
        .catch(err => {
          console.error("PUT FALURE", err.response);
          this.groupDialog.saveLoading = false;
          eventBus.$emit("message", {
            content: this.$t("groups.messages.error-editing-group")
          });
        });
    },

    postGroup(newGroup) {
      return this.$http
        .post("/api/v1/groups/groups", newGroup, {
          noErrorSnackBar: true
        })
        .then(resp => {
          this.groups.push(resp.data);
          this.groupDialog.saveLoading = false;
          eventBus.$emit("message", {
            content: this.$t("groups.messages.group-added")
          });
        })
        .catch(err => {
          console.error("POST FAILURE", err.response);
          this.groupDialog.saveLoading = false;
          eventBus.$emit("error", {
            content: this.$t("groups.messages.error-adding-group")
          });
        });
    },

    closeDialog() {
      this.groupDialog.show = false;
    },

    editGroup(group) {
      let groupInfo = pick(group, ["name", "description", "groupType"]);
      this.groupDialog.editingGroupId = group.id; // save the group id
      this.activateGroupDialog(groupInfo, true);
    },

    activateArchiveDialog(groupId) {
      this.archiveDialog.show = true;
      this.archiveDialog.groupId = groupId;
    },

    confirmArchive(event) {
      this.activateArchiveDialog(event.id);
    },

    cancelArchive() {
      this.archiveDialog.show = false;
    },
    archiveGroup() {
      this.archiveDialog.loading = true;
      const groupId = this.archiveDialog.groupId;
      const idx = this.groups.findIndex(ev => ev.id === groupId);
      this.$http
        .patch(`/api/v1/groups/groups/${groupId}`, { active: false })
        .then(resp => {
          this.groups[idx].active = false;
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          eventBus.$emit("message", {
            content: this.$t("groups.messages.group-archived")
          });
        })
        .catch(err => {
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          eventBus.$emit("message", {
            content: this.$t("groups.messages.error-archiving-group")
          });
        });
    },
    unarchive(group) {
      const idx = this.groups.findIndex(ev => ev.id === group.id);
      const groupId = group.id;
      group.id = -1; // to show loading spinner
      this.$http
        .patch(`/api/v1/groups/groups/${groupId}`, { active: true })
        .then(resp => {
          Object.assign(this.groups[idx], resp.data);
          eventBus.$emit("message", {
            content: this.$t("groups.messages.group-unarchived")
          });
        })
        .catch(err => {
          eventBus.$emit("error", {
            content: this.$t("groups.messages.error-unarchiving-gropu")
          });
        });
    },
    duplicate(group) {
      const copyGroup = JSON.parse(JSON.stringify(group));
      delete copyGroup.id;
      this.activateGroupDialog(copyGroup);
    },
    addAnotherGroup(group) {
      this.saveGroup(group, false);
    },
    showSplitGroupDialog(group) {
      this.splitGroupDialog.parentGroup = group;
      this.splitGroupDialog.show = true;
    },
    hideSplitGroupDialog() {
      this.splitGroupDialog.parentGroup = {};
      this.splitGroupDialog.show = false;
    },
    handleSplitGroupSuccess() {
      this.hideSplitGroupDialog();
      this.fetchGroups();
    }
  }
};
</script>

<style scoped>
.hover-hand {
  cursor: pointer;
}
</style>
