<template>
  <div>
    <v-card flat>
      <v-toolbar flat class="pa-1">
        <v-row no-gutters align="center" justify="space-between">
          <v-col cols="4" md="6">
            <v-text-field
              :append-icon="search ? 'clear' : 'search'"
              @click:append="search = ''"
              :label="$t('actions.search')"
              v-model="search"
            >
            </v-text-field>
          </v-col>
          <v-spacer />
          <template v-if="selection.length === 0">
            <v-col cols="4">
              <v-select :items="viewOptions" v-model="viewStatus"> </v-select>
            </v-col>
            <v-spacer />
            <v-col class="shrink">
              <v-tooltip bottom
                ><template v-slot:activator="{ on }">
                  <v-btn color="primary" fab small @click="expandAll" v-on="on"
                    ><v-icon>unfold_more</v-icon></v-btn
                  >
                </template>
                {{ $t("groups.treeview.expand") }}
              </v-tooltip>
            </v-col>
            <v-col class="shrink">
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
          </template>
          <template v-if="selection.length != 0">
            <v-col class="shrink">
              <v-btn fab small @click="showEmailDialog"
                ><v-icon>email</v-icon></v-btn
              >
            </v-col>
            <v-col class="shrink">
              <v-btn fab small @click="groupTypeTreeviewSelection = []">
                <v-icon>close</v-icon>
              </v-btn>
            </v-col>
          </template>
        </v-row>
      </v-toolbar>
      <v-row no-gutters wrap>
        <v-col>
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
                <v-icon v-if="item.type === 'member'">person</v-icon>
                <v-icon v-else-if="item.type === 'manager'">
                  account_circle
                </v-icon>
                <v-icon v-else-if="item.type === 'group_type'">
                  category</v-icon
                >
                <v-icon v-else-if="item.type === 'group'">
                  group
                </v-icon>
              </template>
            </v-treeview>
          </v-card-text>
        </v-col>
        <v-divider class="hidden-sm-and-down" vertical></v-divider>
        <v-col cols="12" md="6">
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
        </v-col>
      </v-row>
    </v-card>
    <!-- Email dialog -->
    <v-dialog eager v-model="emailDialog.show" max-width="700px">
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
import { uniqBy } from "lodash";
import EmailForm from "../../EmailForm";
export default {
  name: "TreeviewCategory",
  components: { EmailForm },
  props: {
    groups: Array,
    persons: Array,
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
    processedGroups() {
      return this.groups
        ? this.groups
            .filter((group) => group.active)
            .map((group) => ({
              ...group,
              members: group.members.filter((m) => m.active),
              managers: group.managers.filter((m) => m.active),
            }))
        : [];
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
      let all = this.persons
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
      let counter = 0;
      const groupTypes = [];
      let groupTypesMap = {}; // a map from groupTypeId => { name: ..., children: [...] }
      for (let group of this.processedGroups) {
        if (!Object.hasOwnProperty.call(groupTypesMap, group.groupTypeId)) {
          groupTypesMap[group.groupTypeId] = {
            id: counter++,
            name: group.groupType.name,
            children: [],
            type: "group_type",
          };
        }
        // in each group, categorize their people by manager/member
        const managerMember = [];
        if (
          this.viewStatus === "showAll" ||
          this.viewStatus === "showMembers"
        ) {
          const members = [];
          for (let member of group.members) {
            members.push({
              id: counter++,
              name: this.getPersonFullName(member.person),
              obj: member.person,
              type: "member",
            });
          }
          if (members.length > 0) {
            managerMember.push({
              id: counter++,
              name: this.$t("groups.treeview.categories.members"),
              children: members,
              type: "members",
            });
          }
        }
        if (
          this.viewStatus === "showAll" ||
          this.viewStatus === "showManagers"
        ) {
          const managers = [];
          for (let manager of group.managers) {
            managers.push({
              id: counter++,
              name: this.getPersonFullName(manager.person),
              obj: manager.person,
              type: "manager",
            });
          }
          if (managers.length > 0) {
            managerMember.push({
              id: counter++,
              name: this.$t("groups.treeview.categories.managers"),
              children: managers,
              type: "managers",
            });
          }
        }
        if (managerMember.length > 0) {
          groupTypesMap[group.groupTypeId].children.push({
            id: counter++,
            name: group.name,
            children: managerMember,
            type: "group",
          });
        }
      }
      for (let groupTypeId in groupTypesMap) {
        if (groupTypesMap[groupTypeId].children.length > 0) {
          groupTypes.push(groupTypesMap[groupTypeId]);
        }
      }
      return groupTypes;
    },
  },
  methods: {
    /* returns a map in the form of { key1: [item1, item2], key2: [...] } 
    that categorizes each item in list by its key indicated by keyFunc(item)
     each item is added to the list after being transformed by mapFunc */
    categorizeBy(list, keyFunc, mapFunc) {
      const map = {};
      list.forEach((item) => {
        let key = keyFunc(item);
        if (!Object.hasOwnProperty.call(map, key)) {
          map[key] = [];
        }
        map[key].push(mapFunc(item));
      });
      return map;
    },
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
      search: "",
      groupTypeTreeviewSelection: [],
      selectManagers: true,
      selectMembers: true,
    };
  },
};
</script>
<style>
.v-treeview-node__prepend {
  min-width: 0px;
}
</style>
