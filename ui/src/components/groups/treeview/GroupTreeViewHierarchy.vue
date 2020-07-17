<template>
  <div>
    <v-card v-if="cycleError.show" flat>
      <v-card-title class="justify-center">
        <v-alert color="warning">
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-icon v-on="on">error</v-icon>
            </template>
            Please remove the cycle in the node listed in order to view group
            hierarchy tree
          </v-tooltip>
          Unexpected cycle in hierarchy: {{ cycleError.node.toHumanReadable() }}
        </v-alert>
      </v-card-title>
      <v-card-text>
        <v-timeline v-if="cycleError.path.length !== 0">
          <v-timeline-item
            v-for="(node, i) in cycleError.path"
            :key="i"
            :color="node.equal(cycleError.node) ? 'error' : 'primary'"
            :class="i % 2 ? 'text-right' : ''"
          >
            <v-icon v-if="node.nodeType === 'Group'">people</v-icon>
            <v-icon v-else>person</v-icon>
            {{ node.toHumanReadable() }}
          </v-timeline-item>
        </v-timeline>
      </v-card-text>
    </v-card>
    <v-card v-else flat>
      <v-toolbar flat class="pa-1">
        <v-row align-center justify-space-between>
          <v-col md6 xs3>
            <v-text-field
              :append-icon="search ? 'clear' : 'search'"
              @click:append="search = ''"
              :label="$t('actions.search')"
              v-model="search"
            >
            </v-text-field>
          </v-col>
          <v-spacer></v-spacer>
          <v-col shrink>
            <v-tooltip bottom
              ><template v-slot:activator="{ on }">
                <v-col shrink>
                  <v-btn color="primary" fab small @click="expandAll" v-on="on"
                    ><v-icon>unfold_more</v-icon></v-btn
                  >
                </v-col>
              </template>
              {{ $t("groups.treeview.expand") }}
            </v-tooltip>
          </v-col>
          <v-col shrink>
            <v-tooltip bottom
              ><template v-slot:activator="{ on }">
                <v-btn
                  color="grey lighten-2"
                  fab
                  small
                  @click="closeAll"
                  v-on="on"
                  ><v-icon>unfold_less</v-icon></v-btn
                >
              </template>
              {{ $t("groups.treeview.collapse") }}
            </v-tooltip>
          </v-col>
        </v-row>
      </v-toolbar>
      <v-card-text>
        <v-treeview
          :items="adminTree"
          :search="search"
          ref="treeview"
          activatable
          transition
          hoverable
          open-on-click
          return-object
        >
          <template v-slot:prepend="{ item }">
            <v-icon v-if="item.nodeType === 'Group'" color="primary"
              >group</v-icon
            >
            <v-icon v-else-if="item.nodeType === 'Participant'">person</v-icon>
            <v-icon v-else-if="item.nodeType === 'Admin'"
              >supervised_user_circle</v-icon
            >
          </template>
          <template v-slot:label="{ item }">
            <router-link
              v-if="item.nodeType === 'Group'"
              :to="{ name: 'group', params: { group: item.info.id } }"
              >{{ item.name }}</router-link
            >
            <span v-else>{{ item.name }}</span>
          </template>
        </v-treeview>
      </v-card-text>
    </v-card>
  </div>
</template>
<script>
import {
  Group,
  Participant,
  count,
  convertToGroupMap,
  getInfoTree,
  HierarchyCycleError,
  isRootNode,
} from "../../../models/GroupHierarchyNode.ts";
import { eventBus } from "../../../plugins/event-bus.js";
export default {
  data() {
    return {
      search: "",
      groups: null /* mark initial state */,
      persons: null,
      cycleError: {
        show: false,
        path: [],
        node: null,
      },
    };
  },
  methods: {
    fetchGroups() {
      return this.$http.get("api/v1/groups/groups").then((resp) => {
        this.groups = resp.data;
      });
    },
    fetchPersons() {
      return this.$http.get("api/v1/people/persons").then((resp) => {
        this.persons = resp.data;
      });
    },
    expandAll() {
      this.$refs["treeview"].updateAll(true);
    },
    closeAll() {
      this.$refs["treeview"].updateAll(false);
    },
  },
  computed: {
    groupMap() {
      return this.groups === null ? {} : convertToGroupMap(this.groups);
    },
    adminMode() {
      // TODO: check whether the current user is an admin */
      return true;
    },
    treeItems() {
      return this.adminMode ? this.adminTree : this.managerTree;
    },
    managerTree() {
      // TODO: returns a tree according to the current user's subgroups
      return [];
    },
    adminTree() {
      const adminNode = { name: "Admin", children: [], nodeType: "Admin" };
      if (this.groups === null || this.persons === null) {
        return [adminNode];
      }
      let counter = count();
      // get all root groups and root participants
      let rootNodes = [
        ...this.groups.map(
          (groupObject) => new Group(groupObject, this.groupMap)
        ),
        ...this.persons.map(
          (person) => new Participant({ person }, this.groupMap)
        ),
      ].filter((node) => isRootNode(node));
      rootNodes.forEach((rootNode) => {
        try {
          adminNode.children.push(getInfoTree(rootNode, false, counter));
        } catch (err) {
          if (err instanceof HierarchyCycleError) {
            this.cycleError.show = true;
            this.cycleError.node = err.node;
            this.cycleError.path = err.path.reverse();
            eventBus.$emit("error", {
              content: err.message,
            });
          } else {
            throw err;
          }
        }
      });
      console.log("adminNode", adminNode);
      return [adminNode];
    },
  },
  mounted() {
    this.fetchGroups();
    if (this.adminMode) {
      this.fetchPersons();
    }
  },
};
</script>
