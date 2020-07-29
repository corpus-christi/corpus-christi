<template>
  <div>
    <v-toolbar flat>
      <v-toolbar-title>{{ $t("groups.treeview.title") }}</v-toolbar-title>
      <v-spacer />
      <v-btn color="primary" :to="{ name: 'all-groups' }">
        <v-icon>list</v-icon>
        {{ $t("groups.treeview.show-list") }}
      </v-btn>
      <template v-slot:extension>
        <v-tabs v-model="currentTab" centered>
          <v-tab>
            {{ $t("groups.treeview.category-view") }}
          </v-tab>
          <v-tab>
            {{ $t("groups.treeview.hierarchy-view") }}
          </v-tab>
        </v-tabs>
      </template>
    </v-toolbar>
    <v-container v-if="loading">
      <v-skeleton-loader type="date-picker-options" />
      <v-skeleton-loader type="text" />
    </v-container>
    <v-tabs-items v-else-if="isOverseerOrAdmin" v-model="currentTab">
      <v-tab-item
        ><treeview-category :groups="groups" :persons="persons"
      /></v-tab-item>
      <v-tab-item
        ><treeview-hierarchy
          :groups="groups"
          :persons="persons"
          :isAdminMode="isAdminMode"
      /></v-tab-item>
    </v-tabs-items>
    <v-container v-else>
      <v-alert type="warning" prominent>
        {{ $t("groups.treeview.no-groups-available") }}
      </v-alert>
    </v-container>
  </div>
</template>
<script>
import TreeviewCategory from "./GroupTreeViewCategory";
import TreeviewHierarchy from "./GroupTreeViewHierarchy";
import { unionBy } from "lodash";
import { mapState } from "vuex";
import {
  convertToGroupMap,
  getParticipantById,
  getAllSubGroups,
} from "../../../models/GroupHierarchyNode.ts";
export default {
  components: { TreeviewCategory, TreeviewHierarchy },
  data() {
    return {
      currentTab: null,
      allGroups: [],
      loading: true,
    };
  },
  computed: {
    groupMap() {
      return convertToGroupMap(this.allGroups);
    },
    isAdminMode() {
      return this.currentAccount.roles.includes("role.group-admin");
    },
    isOverseerOrAdmin() {
      return this.isAdminMode || this.groups.length > 0;
    },
    groups() {
      if (this.isAdminMode) {
        return this.allGroups;
      } else {
        let currentParticipant = getParticipantById(
          this.currentAccount.id,
          this.groupMap
        );
        return currentParticipant
          ? getAllSubGroups(currentParticipant).map((group) =>
              group.getObject()
            )
          : [];
      }
    },
    // a duplicate-free list of persons in all groups
    persons() {
      let groupParticipants = this.groups.map((g) =>
        unionBy(g.members, g.managers, (m) => m.person.id)
      );
      let all = unionBy(...groupParticipants, (m) => m.person.id).map(
        (m) => m.person
      );
      return all;
    },
    ...mapState(["currentAccount"]),
  },
  methods: {
    fetchGroups() {
      return this.$http.get("api/v1/groups/groups").then((resp) => {
        this.allGroups = resp.data;
      });
    },
  },
  mounted() {
    this.fetchGroups().then(() => {
      this.loading = false;
    });
  },
};
</script>
