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
          ></v-text-field>
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
        <v-flex shrink justify-self-end>
          <v-btn
            color="primary"
            raised
            v-on:click.stop="newGroup"
            data-cy="add-event"
          >
            <v-icon dark left>add</v-icon>
            {{ $t("actions.add-group") }}
          </v-btn>
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
          v-on:click="$router.push({ path: '/groups/' + props.item.id })"
        >
          <span> {{ props.item.name }}</span>
        </td>
        <td
          class="hover-hand"
          v-on:click="$router.push({ path: '/groups/' + props.item.id })"
        >
          {{ props.item.description }}
        </td>
        <td>
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

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false">
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>
  </div>
</template>

<script>
import GroupForm from "./GroupForm";
export default {
  components: { "group-form": GroupForm },
  name: 'GroupTable',
  mounted() {
    this.tableLoading = true;
    this.$http.get("/api/v1/groups/groups").then(resp => {
      this.groups = resp.data;
      this.tableLoading = false;
    });
    this.onResize();
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
        sortBy: "start", //default sorted column
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
        group: {}
      },

      snackbar: {
        show: false,
        text: ""
      },
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

      if (this.viewStatus == "viewActive") {
        return list.filter(ev => ev.active);
      } else if (this.viewStatus == "viewArchived") {
        return list.filter(ev => !ev.active);
      } else {
        return list;
      }
    },

    headers() {
      return [
        { text: this.$t("groups.name"), value: "name" },
        { text: this.$t("groups.decription"), value: "description" },
        { text: this.$t("groups.actions"), sortable: false }
      ];
    },
  },

  methods: {
    activateGroupDialog(group = {}, editMode = false) {
      this.groupDialog.editMode = editMode;
      this.groupDialog.group = group;
      this.groupDialog.show = true;
    },
    newGroup() {
      this.activateGroupDialog();
    },

    cancelGroup() {
      this.groupDialog.show = false;
    },

    saveGroup(group) {
      this.groupDialog.saveLoading = true;
      console.log(group)
      if (group.manager) {
        group.manager_id = group.manager.id;
      }
      let newGroup = JSON.parse(JSON.stringify(group));
      delete newGroup.manager;
      delete newGroup.id;
      if (this.groupDialog.editMode) {
        const groupId = group.id;
        const idx = this.groups.findIndex(ev => ev.id === group.id);
        this.$http
          .put(`/api/v1/groups/${groupId}`, newGroup)
          .then(resp => {
            console.log("EDITED", resp);
            Object.assign(this.groups[idx], resp.data);
            this.groupDialog.show = false;
            this.groupDialog.saveLoading = false;
            this.showSnackbar(this.$t("groups.group-edited"));
          })
          .catch(err => {
            console.error("PUT FALURE", err.response);
            this.groupDialog.saveLoading = false;
            this.showSnackbar(this.$t("groups.error-editing-group"));
          });
      } else {
        this.$http
          .post("/api/v1/groups/groups", newGroup)
          .then(resp => {
            console.log("ADDED", resp);
            this.groups.push(resp.data);
            this.groupDialog.show = false;
            this.groupDialog.saveLoading = false;
            this.showSnackbar(this.$t("groups.event-added"));
          })
          .catch(err => {
            console.error("POST FAILURE", err.response);
            this.groupDialog.saveLoading = false;
            this.showSnackbar(this.$t("groups.error-adding-event"));
          });
      }
    },

    editGroup(group) {
      this.activateGroupDialog({ ...group }, true);
    },

    addAnotherGroup() {

    },

    onResize() {
      this.windowSize = { x: window.innerWidth, y: window.innerHeight };
      if (this.windowSize.x <= 960) {
        this.windowSize.small = true;
      } else {
        this.windowSize.small = false;
      }
    },
    
    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },

  }
}
</script>