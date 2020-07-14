<template>
  <div>
    <v-card flat>
      <v-toolbar card class="pa-1" :color="toolbarColor">
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
          <template v-if="selection.length === 0">
            <v-flex md3 xs4>
              <v-select :items="viewOptions" v-model="viewStatus"> </v-select>
            </v-flex>
            <v-flex shrink>
              <v-tooltip bottom
                ><template v-slot:activator="{ on }">
                  <v-flex shrink>
                    <v-btn
                      color="primary"
                      fab
                      small
                      @click="expandAll"
                      v-on="on"
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
          </template>
          <template v-if="selection.length != 0">
            <v-flex shrink>
              <v-btn fab small @click="showEmailDialog"
                ><v-icon> email </v-icon></v-btn
              >
            </v-flex>
            <v-flex shrink>
              <v-btn fab small @click="groupTypeTreeviewSelection = []">
                <v-icon> close</v-icon>
              </v-btn>
            </v-flex>
          </template>
        </v-layout>
      </v-toolbar>
      <v-layout wrap>
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
        <v-divider class="hidden-sm-and-down" vertical></v-divider>
        <v-flex md6 sm12>
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
    <!-- Email dialog -->
    <v-dialog v-model="emailDialog.show" max-width="700px">
      <email-form
        :initialData="emailInitialData"
        @sent="hideEmailDialog"
        @error="hideEmailDialog"
        @cancel="hideEmailDialog"
      ></email-form>
    </v-dialog>
  </div>
</template>

<script>
import { unionBy, uniqBy } from "lodash";
import EmailForm from "../../EmailForm";
export default {
  name: "GroupTreeView",
  components: { EmailForm },
  mounted() {
    this.$http.get("/api/v1/groups/groups").then((resp) => {
      this.groups = resp.data.filter((group) => group.active);
      this.groups.forEach((group) => {
        group.members = group.members.filter((member) => member.active);
        group.managers = group.managers.filter((manager) => manager.active);
      });
    });
  },
  computed: {
    viewOptions() {
      return [
        { text: this.$t("groups.treeview.show-all"), value: "showAll" },
        {
          text: this.$t("groups.treeview.show-managers"),
          value: "showManagers",
        },
        { text: this.$t("groups.treeview.show-members"), value: "showMembers" },
      ];
    },
    toolbarColor() {
      return this.selection.length == 0 ? undefined : "blue-grey";
    },
    allPeople() {
      // a duplicate-free list of persons in all groups
      let groupParticipants = this.groups.map((g) =>
        unionBy(g.members, g.managers, (m) => m.person.id)
      );
      let all = unionBy(...groupParticipants, (m) => m.person.id).map(
        (m) => m.person
      );
      return all;
    },
    selection() {
      // a duplicate-free list of persons selected in the tree
      let selection = this.groupTypeTreeviewSelection.filter(
        (item) => !item.children
      ); // get rid of intermediate nodes
      selection = uniqBy(selection, (item) => item.obj.id); // remove duplicate
      return selection;
    },
    emailInitialData() {
      let selected = this.selection
        .filter((item) => item.obj.email)
        .map((item) => ({
          ...item.obj,
          name: `${item.obj.firstName} ${item.obj.lastName}`,
        }));
      let all = this.allPeople
        .filter((p) => p.email)
        .map((p) => ({
          ...p,
          name: `${p.firstName} ${p.lastName}`,
        }));
      return {
        recipientList: all,
        recipients: selected,
      };
    },
    groupTypeTreeviewItems() {
      // categorize groups by group type
      const groupTypes = [];
      const root = {
        id: "_label_root",
        name: this.$t("groups.treeview.categories.all-group-types"),
        children: groupTypes,
      };
      let groupTypesMap = {};
      for (let group of this.groups) {
        if (!Object.hasOwnProperty.call(groupTypesMap, group.groupTypeId)) {
          groupTypesMap[group.groupTypeId] = {
            id: `_group_type_${group.groupTypeId}`,
            name: group.groupType.name,
            children: [],
          };
        }
        // in each group, categorize their people by manager/member
        const managerMember = [];
        groupTypesMap[group.groupTypeId].children.push({
          id: `_group_${group.id}`,
          name: group.name,
          children: managerMember,
        });
        if (
          this.viewStatus === "showAll" ||
          this.viewStatus === "showMembers"
        ) {
          const members = [];
          managerMember.push({
            id: `_label_group_${group.id}_members`,
            name: this.$t("groups.treeview.categories.members"),
            children: members,
          });
          for (let member of group.members) {
            members.push({
              id: `group_member_${group.id}_${member.person.id}`,
              name: this.getPersonFullName(member.person),
              obj: member.person,
            });
          }
        }
        if (
          this.viewStatus === "showAll" ||
          this.viewStatus === "showManagers"
        ) {
          const managers = [];
          managerMember.push({
            id: `_label_group_${group.id}_managers`,
            name: this.$t("groups.treeview.categories.managers"),
            children: managers,
          });
          for (let manager of group.managers) {
            managers.push({
              id: `group_manager_${group.id}_${manager.person.id}`,
              name: this.getPersonFullName(manager.person),
              obj: manager.person,
            });
          }
        }
      }
      for (let groupType in groupTypesMap) {
        groupTypes.push(groupTypesMap[groupType]);
      }
      return [root];
    },
  },
  methods: {
    getPersonFullName(person) {
      return `${person.firstName} ${person.lastName}`;
    },
    expandAll() {
      this.$refs["treeview"].updateAll(true);
    },
    closeAll() {
      this.$refs["treeview"].updateAll(false);
    },
    showEmailDialog() {
      this.emailDialog.show = true;
    },
    hideEmailDialog() {
      this.emailDialog.show = false;
    },
  },
  data() {
    return {
      viewStatus: "showAll",
      showManagers: true,
      showMembers: true,
      emailDialog: {
        show: false,
        loading: false,
      },
      groups: [],
      search: "",
      groupTypeTreeviewSelection: [],
      selectManagers: true,
      selectMembers: true,
    };
  },
};
</script>
