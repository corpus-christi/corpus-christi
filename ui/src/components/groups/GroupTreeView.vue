<template>
  <v-card>
    <v-toolbar class="pa-1" :color="toolbarColor">
      <v-layout align-center>
        <v-flex md2
          ><v-toolbar-title>{{
            $t("groups.treeview.title")
          }}</v-toolbar-title></v-flex
        >
        <v-flex md4>
          <v-text-field
            :append-icon="search ? 'clear' : 'search'"
            @click:append="search = ''"
            :label="$t('actions.search')"
            v-model="search"
          >
          </v-text-field>
        </v-flex>
        <v-spacer></v-spacer>

        <v-layout align-center v-if="selection.length == 0">
          <v-flex>
            <v-select :items="viewOptions" v-model="viewStatus"> </v-select>
          </v-flex>
          <v-spacer></v-spacer>
          <v-flex>
            <v-btn color="primary" fab small @click="expandAll"
              ><v-icon>unfold_more</v-icon></v-btn
            >
          </v-flex>
          <v-flex>
            <v-btn color="grey lighten-2" fab small @click="closeAll"
              ><v-icon>unfold_less</v-icon></v-btn
            >
          </v-flex>
          <v-flex>
            <v-btn color="primary" raised :to="{ name: 'all-groups' }">
              <v-icon dark left>list</v-icon>
              {{ $t("groups.treeview.show-list") }}
            </v-btn>
          </v-flex>
        </v-layout>
        <v-layout v-else align-center justify-end>
          <v-flex shrink>
            <v-btn fab small><v-icon> email </v-icon></v-btn>
          </v-flex>
          <v-flex shrink>
            <v-btn fab small @click="groupTypeTreeviewSelection = []">
              <v-icon> close</v-icon>
            </v-btn>
          </v-flex>
        </v-layout>
      </v-layout>
    </v-toolbar>
    <v-layout>
      <v-flex>
        <v-card-text>
          <v-treeview
            v-model="groupTypeTreeviewSelection"
            :search="search"
            :items="groupTypeTreeviewItems"
            selectable
            transition
            hoverable
            open-on-click
            return-object
            ref="treeview"
          >
            <template v-slot:prepend="{ item }">
              <v-icon v-if="item.id.match(/^group_member/)"> person </v-icon>
              <v-icon v-else-if="item.id.match(/^group_manager/)">
                account_circle
              </v-icon>
              <v-icon v-else-if="item.id.match(/^_group_type/)">
                category</v-icon
              >
              <v-icon v-else-if="item.id.match(/^_group_[0-9]/)">
                group
              </v-icon>
            </template>
          </v-treeview>
        </v-card-text>
      </v-flex>
      <v-divider vertical></v-divider>
      <v-flex cols="12" md6>
        <v-card-text>
          <div
            v-if="selection.length == 0"
            class="title pa-4 text-center grey--text"
          >
            {{ $t("groups.treeview.select-placeholder") }}
          </div>
          <v-scroll-x-transition group hide-on-leave>
            <v-chip v-for="item in selection" :key="item.id">{{
              item.name
            }}</v-chip>
          </v-scroll-x-transition>
        </v-card-text>
      </v-flex>
    </v-layout>
  </v-card>
</template>

<script>
import { unionBy, uniqBy } from "lodash";
export default {
  name: "GroupTreeView",
  mounted() {
    this.$http.get("/api/v1/groups/groups").then(resp => {
      this.groups = resp.data;
    });
  },
  computed: {
    toolbarColor() {
      return this.selection.length == 0 ? undefined : "blue-grey";
    },
    selection() {
      // a duplicate-free list of persons selected in the tree
      let selection = this.groupTypeTreeviewSelection.filter(
        item => !item.children
      ); // get rid of intermediate nodes
      selection = uniqBy(selection, item => item.obj.id); // remove duplicate
      return selection;
    },
    groupTypeTreeviewItems() {
      // categorize groups by group type
      const groupTypes = [];
      const root = {
        id: "_label_root",
        name: this.$t("groups.treeview.categories.all-group-types"),
        children: groupTypes
      };
      let groupTypesMap = {};
      for (let group of this.groups) {
        if (!Object.hasOwnProperty.call(groupTypesMap, group.groupTypeId)) {
          groupTypesMap[group.groupTypeId] = {
            id: `_group_type_${group.groupTypeId}`,
            name: group.groupType.name,
            children: []
          };
        }
        // in each group, categorize their people by manager/member
        const managerMember = [];
        groupTypesMap[group.groupTypeId].children.push({
          id: `_group_${group.id}`,
          name: group.name,
          children: managerMember
        });
        if (this.viewStatus == "showAll" || this.viewStatus == "showMembers") {
          const members = [];
          managerMember.push({
            id: `_label_group_${group.id}_members`,
            name: this.$t("groups.treeview.categories.members"),
            children: members
          });
          for (let member of group.members) {
            members.push({
              id: `group_member_${group.id}_${member.person.id}`,
              name: this.getPersonFullName(member.person),
              obj: member.person
            });
          }
        }
        if (this.viewStatus == "showAll" || this.viewStatus == "showManagers") {
          const managers = [];
          managerMember.push({
            id: `_label_group_${group.id}_managers`,
            name: this.$t("groups.treeview.categories.managers"),
            children: managers
          });
          for (let manager of group.managers) {
            managers.push({
              id: `group_manager_${group.id}_${manager.person.id}`,
              name: this.getPersonFullName(manager.person),
              obj: manager.person
            });
          }
        }
      }
      for (let groupType in groupTypesMap) {
        groupTypes.push(groupTypesMap[groupType]);
      }
      return [root];
    }
  },
  methods: {
    getPersonFullName(person) {
      return `${person.firstName} ${person.lastName}`;
    },
    getImmSubGroups(group) {
      /* get immediate subgroups.
      Immediate subgroups are defined as a unique collection of groups led by any of the members/managers of the current group.
      group: {
        id: 1,
        members: [ { person: { managers: [ { groupId: 4, active: true }, ... ], ... }, ...}, ... ],
        managers: [ { person: { managers: [ { groupId: 5, ... }, ... ], ... }, ...}, ... ],
        ...
      }
       */
      let people = group.members.concat(group.managers);
      people = people.map(p => p.person.managers);
      let uniqueGroups = unionBy(...people, g => g.groupId);
      uniqueGroups = uniqueGroups.filter(g => g.active);
      return uniqueGroups;
    },
    // getSubGroups(groups, group, subGroups = []) {
    //   /* returns all groups in 'groups' subordinate to 'group', according to the leadership hierarchy
    //   pseudocode:
    //     for all `members` and `managers` in `group`, get their leading groups;
    //     if all of their leading groups are in `subGroups`, then return `subGroups`.
    //     Otherwise, build a new list of groups, `extraGroups`, consisting of unique leading groups that are not in `subGroups`;
    //     return a list of unique groups consisting of groups in `subGroups` and getSubGroups(g) for g in extraGroups.
    //   groups is an array of all groups, each group is an object of the following form:
    //   group: {
    //     id: 1,
    //     members: [ { person: { managers: [ { groupId: 4, active: true }, ... ], ... }, ...}, ... ],
    //     managers: [ { person: { managers: [ { groupId: 5, ... }, ... ], ... }, ...}, ... ],
    //     ...
    //   }
    //    */
    //   const groupsMap = {}; // build a dictionary so we can index with id
    //   for (let g of groups) {
    //     groupsMap[g.id] = g;
    //   }
    //   subGroupIds = subGroups.map(g => g.id);
    // },
    // _getSubGroupsIds(groups, groupId, subGroupIds) {
    //   /* a helper function for getSubGroups, returns a list of ids */
    // },
    expandAll() {
      this.$refs["treeview"].updateAll(true);
    },
    closeAll() {
      this.$refs["treeview"].updateAll(false);
    }
  },
  data() {
    return {
      viewOptions: [
        { text: this.$t("groups.treeview.show-all"), value: "showAll" },
        {
          text: this.$t("groups.treeview.show-managers"),
          value: "showManagers"
        },
        { text: this.$t("groups.treeview.show-members"), value: "showMembers" }
      ],
      viewStatus: "showAll",
      showManagers: true,
      showMembers: true,
      groups: [],
      search: "",
      groupTypeTreeviewSelection: [],
      selectManagers: true,
      selectMembers: true
    };
  }
};
</script>
