<template>
  <div>
    {{ selection }}
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
                <v-icon
                  v-else-if="
                    item.type === 'groupType' || item.type === 'managerType'
                  "
                >
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
    /*** view/selection related ***/
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
    groupTypeMap() {
      return this.categorizeBy(
        this.processedGroups,
        (group) => group.groupTypeId
      );
    },
    groupTypeTreeviewItems() {
      let counter = 0;
      let groupTypesChildrenMap = this.categorizeBy(
        this.processedGroups,
        (group) => group.groupType.name, // collapse group types that have the same name
        (group) => {
          let managersChildrenMap = this.categorizeBy(
            group.managers,
            (manager) => manager.managerType.name, // collapse manager types that have the same name
            (manager) => ({
              id: counter++,
              name: this.getPersonFullName(manager.person),
              obj: manager.person,
              type: "manager",
            })
          );
          let managersChildren = this.mapToNodes(
            managersChildrenMap,
            (managerTypeName, managerNodes) => ({
              id: counter++,
              name: managerTypeName,
              type: "managerType",
              children: managerNodes,
            })
          );
          let managersNode = managersChildren.length
            ? {
                id: counter++,
                name: this.$t("groups.treeview.categories.managers"),
                type: "managers",
                children: managersChildren,
              }
            : null;
          let membersChildren = group.members.map((member) => ({
            id: counter++,
            name: this.getPersonFullName(member.person),
            obj: member.person,
            type: "member",
          }));
          let membersNode = membersChildren.length
            ? {
                id: counter++,
                name: this.$t("groups.treeview.categories.members"),
                type: "members",
                children: membersChildren,
              }
            : null;
          let groupChildren = [
            ...(membersNode ? [membersNode] : []),
            ...(managersNode ? [managersNode] : []),
          ];
          return {
            id: counter++,
            name: group.name,
            type: "group",
            children: groupChildren,
          };
        }
      );
      let groupTypesChildren = this.mapToNodes(
        groupTypesChildrenMap,
        (groupTypeName, groupNodes) => ({
          id: counter++,
          name: groupTypeName,
          type: "groupType",
          children: groupNodes.filter((groupNode) => groupNode.children.length),
        })
      );
      let groupTypesNode = {
        id: counter++,
        name: this.$t("groups.treeview.categories.all-group-types"),
        type: "groupTypes",
        children: groupTypesChildren,
      };
      return [groupTypesNode];
    },

    /*** email related ***/
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
  },
  methods: {
    /* returns a map in the form of { key1: [item1, item2], key2: [...] }
    that categorizes each item in list by its key indicated by keyFunc(item)
     each item is added to the list after being transformed by mapFunc */
    categorizeBy(list, keyFunc, mapFunc = (item) => item) {
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
    /* convert a map to a list of nodes */
    mapToNodes(map, makeNode) {
      let nodes = [];
      Object.entries(map).forEach(([key, value]) => {
        nodes.push(makeNode(key, value));
      });
      return nodes;
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
