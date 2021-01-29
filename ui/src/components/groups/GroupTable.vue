<template>
  <div>
    <v-toolbar class="pa-1">
      <v-row align="center" justify="space-between" fill-height>
        <v-col class="shrink" cols="2">
          <v-toolbar-title>{{ $t("groups.header") }}</v-toolbar-title>
        </v-col>
        <v-col>
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="$t('actions.search')"
            single-line
            hide-details
            data-cy="form-search"
          />
        </v-col>
        <template v-if="isAdmin">
          <v-col>
            <v-select
              hide-details
              solo
              single-line
              :items="viewOptions"
              v-model="viewStatus"
              data-cy="view-status-select"
            >
            </v-select>
          </v-col>
        </template>
        <v-col class="shrink">
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
                  $vuetify.breakpoint.mdAndDown
                    ? ""
                    : isAdmin
                    ? $t("groups.admin-panel")
                    : $t("groups.user-panel")
                }}
              </v-btn>
            </template>
            <v-list>
              <template v-if="isAdmin">
                <v-list-item @click.stop="activateGroupDialog()">
                  <v-icon color="primary">group_add</v-icon>
                  <v-list-item-content>
                    {{ $t("actions.add-group") }}
                  </v-list-item-content>
                </v-list-item>
                <v-list-item :to="{ name: 'group-types' }">
                  <v-icon color="primary">view_list</v-icon>
                  <v-list-item-content>
                    {{ $t("groups.entity-types.group-types.manage") }}
                  </v-list-item-content>
                </v-list-item>
                <v-list-item :to="{ name: 'manager-types' }">
                  <v-icon color="primary">view_list</v-icon>
                  <v-list-item-content>
                    {{ $t("groups.entity-types.manager-types.manage") }}
                  </v-list-item-content>
                </v-list-item>
              </template>
              <template>
                <v-list-item
                  :to="{ name: 'group-treeview' }"
                  data-cy="show-treeview"
                >
                  <v-icon color="primary">account_tree</v-icon>
                  <v-list-item-content>
                    {{ $t("groups.treeview.show-treeview") }}
                  </v-list-item-content>
                </v-list-item>
              </template>
              <v-list-item
                :to="{ name: 'group-lineGraph' }"
                data-cy="show-linegraph"
              >
                <v-icon color="primary">multiline_chart</v-icon>
                <v-list-item-content>
                  {{ $t("groups.treeview.show-linegraph") }}
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-col>
      </v-row>
    </v-toolbar>

    <!-- Table of existing groups -->
    <v-data-table
      :headers="headers"
      :items-per-page-options="itemsPerPageOptions"
      :items="visibleGroups"
      :search="search"
      :loading="tableLoading"
      :options.sync="options"
      @click:row="navigateToGroup($event.id)"
      must-sort
      :item-class="itemClass"
      class="elevation-1"
      hide-default-footer
      @page-count="pageCount = $event"
      :page.sync="page"
    >
      <template v-slot:[`item.actions`]="props">
        <template v-if="props.item.active">
          <v-tooltip bottom>
            <template v-slot:activator="{ on }"
              ><v-btn
                v-on="on"
                icon
                outlined
                small
                color="primary"
                v-on:click.stop="editGroup(props.item)"
                data-cy="edit"
              >
                <v-icon small>edit</v-icon>
              </v-btn></template
            >
            <span>{{ $t("actions.edit") }}</span>
          </v-tooltip>
          <v-tooltip bottom>
            <template v-slot:activator="{ on }"
              ><v-btn
                v-on="on"
                icon
                outlined
                small
                color="primary"
                v-on:click.stop="duplicate(props.item)"
                data-cy="duplicate"
              >
                <v-icon small>filter_none</v-icon>
              </v-btn></template
            >
            <span>{{ $t("actions.duplicate") }}</span>
          </v-tooltip>
          <v-tooltip bottom>
            <template v-slot:activator="{ on }"
              ><v-btn
                v-on="on"
                icon
                outlined
                small
                color="primary"
                v-on:click.stop="showSplitGroupDialog(props.item)"
                data-cy="split"
              >
                <v-icon small>call_split</v-icon>
              </v-btn></template
            >
            <span>{{ $t("groups.split.tooltip") }}</span>
          </v-tooltip>
          <v-tooltip bottom>
            <template v-slot:activator="{ on }"
              ><v-btn
                v-on="on"
                icon
                outlined
                small
                color="primary"
                v-on:click.stop="sendEmail(props.item)"
                data-cy="email"
              >
                <v-icon small>email</v-icon>
              </v-btn></template
            >
            <span>{{ $t("groups.batch-actions.email") }}</span>
          </v-tooltip>
          <v-tooltip bottom>
            <template v-slot:activator="{ on }"
              ><v-btn
                v-on="on"
                icon
                outlined
                small
                color="primary"
                v-on:click.stop="confirmArchive(props.item)"
                data-cy="archive"
              >
                <v-icon small>archive</v-icon>
              </v-btn></template
            >
            <span>{{ $t("actions.tooltips.archive") }}</span>
          </v-tooltip>
        </template>
        <template v-else>
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <span class="d-inline-block" v-on="on">
                <v-btn
                  :disabled="props.item.isCyclingGroup"
                  icon
                  outlined
                  small
                  color="primary"
                  v-on:click.stop="unarchive(props.item)"
                  :loading="props.item.id < 0"
                  data-cy="unarchive"
                >
                  <v-icon small>undo</v-icon>
                </v-btn>
              </span>
            </template>
            <span>{{
              props.item.isCyclingGroup
                ? $t(
                    "groups.batch-actions.messages.unarchive-group-will-cause-cycle"
                  )
                : $t("actions.tooltips.activate")
            }}</span>
          </v-tooltip>
        </template>
      </template>
    </v-data-table>
    <div class="text-center pt-2">
      <v-pagination v-model="page" :length="pageCount"></v-pagination>
    </div>

    <!-- New/Edit dialog -->
    <v-dialog eager v-model="groupDialog.show" max-width="500px" persistent>
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
            text
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
    <v-dialog
      eager
      v-model="splitGroupDialog.show"
      max-width="1300px"
      persistent
    >
      <split-group-form
        @cancel="hideSplitGroupDialog"
        @success="handleSplitGroupSuccess"
        @error="hideSplitGroupDialog"
        :initial-data="splitGroupDialog.parentGroup"
      />
    </v-dialog>

    <!-- Email Dialog -->
    <v-dialog eager v-model="emailDialog.show" max-width="1300px" persistent>
      <email-form
        v-bind:initialData="emailDialog.recipientData"
        v-on:cancel="cancelEmail"
        v-on:sent="cancelEmail"
      ></email-form>


    </v-dialog>
  </div>
</template>

<script>
import GroupForm from "./GroupForm";
import SplitGroupForm from "./SplitGroupForm";
import { eventBus } from "@/plugins/event-bus";
import { pick } from "lodash";
import EmailForm from "../EmailForm"
import {
  convertToGroupMap,
  Group,
  getTree,
  HierarchyCycleError,
} from "@/models/GroupHierarchyNode";
import { mapState } from "vuex";

export default {
  components: { GroupForm, SplitGroupForm, "email-form": EmailForm },
  name: "GroupTable",
  mounted() {
    this.fetchGroups();
  },
  data() {
    return {
      page: 1,
      pageCount: 0,

      itemsPerPageOptions: [
        10,
        15,
        25,
        { text: "$vuetify.dataIterator.rowsPerPageAll", value: -1 },
      ],
      options: {
        sortBy: ["activeMembers.length"], //default sorted column
        sortDesc: [true],
        itemsPerPage: 10,
        page: 1,
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
        group: {},
      },
      emailDialog: {
        show: false,
        saveLoading: false,
        group: {},
        recipientData: {},
      },
      archiveDialog: {
        show: false,
        groupId: -1,
        loading: false,
      },
      splitGroupDialog: {
        show: false,
        parentGroup: {},
      },
    };
  },

  computed: {
    viewOptions() {
      return [
        { text: this.$t("actions.view-active"), value: "viewActive" },
        {
          text: this.$t("actions.view-archived"),
          value: "viewArchived",
        },
        { text: this.$t("actions.view-all"), value: "viewAll" },
      ];
    },

    groupMap() {
      return convertToGroupMap(this.groups);
    },

    processedGroups() {
      return this.groups.map((group) => {
        // add an 'activeMembers' property that has all active members
        let activeMembers = group.members.filter((m) => m.active);
        // for each inactive group, also calculate whether activating the group
        // would create a cycle in the leadership hierarchy, indicate by 'isCyclingGroup'
        let isCyclingGroup = false;
        if (!group.active) {
          // hypothesized groupMap with the current group being active
          let hypothesizedGroupMap = {
            ...this.groupMap,
            [group.id]: { ...group, active: true },
          };
          let groupInstance = new Group(
            hypothesizedGroupMap[group.id],
            hypothesizedGroupMap
          );
          try {
            // if a tree can be drawn from the current node, then it is a valid node
            getTree(groupInstance);
          } catch (err) {
            if (err instanceof HierarchyCycleError) {
              isCyclingGroup = true;
            } else {
              throw err;
            }
          }
        }
        return {
          ...group,
          activeMembers,
          isCyclingGroup,
        };
      });
    },

    visibleGroups() {
      let list = this.processedGroups;

      if (this.viewStatus === "viewActive") {
        return list.filter((ev) => ev.active);
      } else if (this.viewStatus === "viewArchived") {
        return list.filter((ev) => !ev.active);
      } else {
        return list;
      }
    },
    headers() {
      let headers = [
        { text: this.$t("groups.name"), value: "name" },
        { text: this.$t("groups.description"), value: "description" },
        {
          text: this.$t("groups.member-count"),
          value: "activeMembers.length",
        },
        { text: this.$t("groups.group-type"), value: "groupType.name" },
      ];
      if (this.isAdmin) {
        headers.push({
          text: this.$t("actions.header"),
          value: "actions",
          sortable: false,
        });
      }
      return headers;
    },
    isAdmin() {
      return this.currentAccount.roles.includes("role.group-admin");
    },
    ...mapState(["currentAccount"]),
  },

  methods: {

    sendEmail(group){
      let recipientList = group.members;
      this.emailDialog.group = group;
      this.emailDialog.recipientData = {
        recipientList,
        recipients: []
      }
      this.emailDialog.show = true
    },

    cancelEmail(){
      this.emailDialog.show = false;
    },

    itemClass() {
      return "hover-hand";
    },
    fetchGroups() {
      this.tableLoading = true;
      this.$http.get("/api/v1/groups/groups").then((resp) => {
        this.groups = resp.data;
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

    navigateToGroup(id) {
      this.$router.push({ name: "group-details", params: { group: id } });
    },

    saveGroup(group, closeDialog = true) {
      this.groupDialog.saveLoading = true;
      let payload = pick(group, ["name", "description"]);
      payload.groupTypeId = group.groupType.id;
      if (this.groupDialog.editMode) {
        this.patchGroup(payload, this.groupDialog.editingGroupId).then(() => {
          let oldGroup = this.groups.find(
            (g) => g.id === this.groupDialog.editingGroupId
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
        .then(() => {
          this.groupDialog.saveLoading = false;
          eventBus.$emit("message", {
            content: "groups.messages.group-edited",
          });
        })
        .catch((err) => {
          console.error("PUT FALURE", err.response);
          this.groupDialog.saveLoading = false;
          eventBus.$emit("error", {
            content: "groups.messages.error-editing-group",
          });
        });
    },

    postGroup(newGroup) {
      return this.$http
        .post("/api/v1/groups/groups", newGroup, {
          noErrorSnackBar: true,
        })
        .then((resp) => {
          this.groups.push(resp.data);
          this.groupDialog.saveLoading = false;
          eventBus.$emit("message", {
            content: "groups.messages.group-added",
          });
        })
        .catch((err) => {
          console.error("POST FAILURE", err.response);
          this.groupDialog.saveLoading = false;
          eventBus.$emit("error", {
            content: "groups.messages.error-adding-group",
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
      const idx = this.groups.findIndex((ev) => ev.id === groupId);
      this.$http
        .patch(`/api/v1/groups/groups/${groupId}`, { active: false })
        .then(() => {
          this.groups[idx].active = false;
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          eventBus.$emit("message", {
            content: "groups.messages.group-archived",
          });
        })
        .catch((err) => {
          console.error("PATCH FAILURE", err.response);
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          eventBus.$emit("error", {
            content: "groups.messages.error-archiving-group",
          });
        });
    },
    unarchive(group) {
      const idx = this.groups.findIndex((ev) => ev.id === group.id);
      const groupId = group.id;
      group.id = -1; // to show loading spinner
      this.$http
        .patch(`/api/v1/groups/groups/${groupId}`, { active: true })
        .then((resp) => {
          Object.assign(this.groups[idx], resp.data);
          eventBus.$emit("message", {
            content: "groups.messages.group-unarchived",
          });
        })
        .catch((err) => {
          console.error("PATCH FAILURE", err.response);
          eventBus.$emit("error", {
            content: "groups.messages.error-unarchiving-group",
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
    },
  },
};
</script>

<style>
/* non-scoped style to make it available to programmatically added classes */
.hover-hand {
  cursor: pointer;
}
</style>
