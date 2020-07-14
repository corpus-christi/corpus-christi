<template>
  <div>
    <v-card flat>
      <v-toolbar card class="pa-1">
        <v-layout align-center justify-space-between>
          <v-flex md6 xs3>
            <v-text-field
              :append-icon="search ? 'clear' : 'search'"
              @click:append="search = ''"
              :label="$t('actions.search')"
              v-model="search"
            >
            </v-text-field>
          </v-flex>
          <v-spacer></v-spacer>
          <v-flex shrink>
            <v-tooltip bottom
              ><template v-slot:activator="{ on }">
                <v-flex shrink>
                  <v-btn color="primary" fab small @click="expandAll" v-on="on"
                    ><v-icon>unfold_more</v-icon></v-btn
                  >
                </v-flex>
              </template>
              {{ $t("groups.treeview.expand") }}
            </v-tooltip>
          </v-flex>
          <v-flex shrink>
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
          </v-flex>
        </v-layout>
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
  isRootNode,
} from "../../../models/GroupHierarchyNode.ts";
export default {
  data() {
    return {
      search: "",
      groups: null /* mark initial state */,
      persons: null,
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
        adminNode.children.push(getInfoTree(rootNode, false, counter));
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
