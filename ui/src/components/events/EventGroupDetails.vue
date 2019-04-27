<template>
  <div>
    <v-card class="ma-1">
      <template v-if="loaded">
        <v-container fill-height fluid>
          <v-flex xs9 sm9 align-end flexbox>
            <span class="headline">{{ $t("groups.title") }}</span>
          </v-flex>
          <v-layout xs3 sm3 align-end justify-end>
            <v-btn
              flat
              color="primary"
              data-cy="add-group-dialog"
              v-on:click="addGroupDialog.show = true"
            >
              <v-icon>add</v-icon>&nbsp;{{ $t("actions.add-group") }}
            </v-btn>
          </v-layout>
        </v-container>
        <v-list v-if="groups.length">
          <template v-for="group in groups">
            <v-divider v-bind:key="'groupDivider' + group.id"></v-divider>
            <v-list-tile v-bind:key="group.id">
              <v-list-tile-content class="pr-0">
                <v-container fluid class="pa-0">
                  <v-layout justify-space-between align-center>
                    <v-flex>{{ group.description }}</v-flex>
                    <v-flex shrink>
                      <v-layout>
                        <v-flex xs6>
                          <!-- TODO: popup with members instead of rerouting -->
                          <v-btn
                            icon
                            outline
                            flat
                            color="primary"
                            :to="{ path: '/groups/' + group.id }"
                            :data-cy="'view-group-' + group.id"
                            ><v-icon>info</v-icon>
                          </v-btn>
                        </v-flex>
                        <v-flex xs6>
                          <v-btn
                            icon
                            outline
                            flat
                            color="primary"
                            v-on:click="showDeleteGroupDialog(group.id)"
                            :data-cy="'deleteGroup-' + group.id"
                            ><v-icon>delete</v-icon>
                          </v-btn>
                        </v-flex>
                      </v-layout>
                    </v-flex>
                  </v-layout>
                </v-container>
              </v-list-tile-content>
            </v-list-tile>
          </template>
        </v-list>
        <div v-else class="text-xs-center pa-4">
          {{ $t("groups.none-assigned") }}
        </div>
      </template>
      <v-layout v-else justify-center height="500px">
        <div class="ma-5 pa-5">
          <v-progress-circular
            indeterminate
            color="primary"
          ></v-progress-circular>
        </div>
      </v-layout>
    </v-card>
    <!-- Add Group dialog -->
    <v-dialog v-model="addGroupDialog.show" persistent max-width="500px">
      <v-card>
        <v-card-title primary-title>
          <span class="headline">{{ $t("actions.add-group") }}</span>
        </v-card-title>
        <v-card-text>
          <entity-search
            data-cy="group-entity-search"
            v-model="addGroupDialog.group"
            :existing-entities="groups"
            group
          ></entity-search>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="closeAddGroupDialog()"
            color="secondary"
            flat
            :disabled="addGroupDialog.loading"
            data-cy="cancel-add"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="addGroup()"
            color="primary"
            raised
            :disabled="!addGroupDialog.group"
            :loading="addGroupDialog.loading"
            data-cy="confirm-add"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- Delete Group dialog -->
    <v-dialog v-model="deleteGroupDialog.show" max-width="350px">
      <v-card>
        <v-card-text>
          <span>{{ $t("groups.confirm-remove-from-event") }}</span>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="deleteGroupDialog.show = false"
            color="secondary"
            flat
            :disabled="deleteGroupDialog.loading"
            data-cy="cancel-delete"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deleteGroup()"
            color="primary"
            raised
            :loading="deleteGroupDialog.loading"
            data-cy="confirm-delete"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>
<script>
import EntitySearch from "../EntitySearch";

export default {
  name: "EventGroupDetails",
  components: {
    "entity-search": EntitySearch
  },

  props: {
    groups: {
      required: true
    },
    loaded: {
      type: Boolean,
      required: true
    }
  },

  data() {
    return {
      addGroupDialog: {
        show: false,
        loading: false,
        group: null
      },

      deleteGroupDialog: {
        show: false,
        loading: false,
        groupId: -1
      }
    };
  },

  methods: {
    closeAddGroupDialog() {
      this.addGroupDialog.loading = false;
      this.addGroupDialog.show = false;
      this.addGroupDialog.group = null;
    },

    addGroup() {
      const eventId = this.$route.params.event;
      let groupId = this.addGroupDialog.group.id;
      const idx = this.groups.findIndex(t => t.id === groupId);
      this.addGroupDialog.loading = true;
      if (idx > -1) {
        this.closeAddGroupDialog();
        this.showSnackbar(this.$t("groups.group-on-event"));
        return;
      }

      this.$http
        .post(`/api/v1/events/${eventId}/groups/${groupId}`)
        .then(() => {
          this.showSnackbar(this.$t("groups.group-added"));
          this.closeAddGroupDialog();
          this.$emit("group-added");
        })
        .catch(err => {
          console.log(err);
          this.addGroupDialog.loading = false;
          if (err.response.status == 422) {
            this.showSnackbar(this.$t("groups.error-group-assigned"));
          } else {
            this.showSnackbar(this.$t("groups.error-adding-group"));
          }
        });
    },

    deleteGroup() {
      let id = this.deleteGroupDialog.groupId;
      const idx = this.groups.findIndex(t => t.id === id);
      this.deleteGroupDialog.loading = true;
      const eventId = this.$route.params.event;
      this.$http
        .delete(`/api/v1/events/${eventId}/groups/${id}`)
        .then(resp => {
          console.log("REMOVED", resp);
          this.deleteGroupDialog.show = false;
          this.deleteGroupDialog.loading = false;
          this.deleteGroupDialog.groupId = -1;
          this.groups.splice(idx, 1); //TODO maybe fix me?
          this.showSnackbar(this.$t("groups.group-removed"));
        })
        .catch(err => {
          console.log(err);
          this.deleteGroupDialog.loading = false;
          this.showSnackbar(this.$t("groups.error-removing-group"));
        });
    },

    showDeleteGroupDialog(groupId) {
      this.deleteGroupDialog.groupId = groupId;
      this.deleteGroupDialog.show = true;
    },

    showSnackbar(message) {
      this.$emit("snackbar", message);
    }
  }
};
</script>
