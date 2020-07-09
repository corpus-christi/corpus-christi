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
          v-if="!$data.$_groupHierarchyMixin_loading"
          :items="$_groupHierarchyMixin_adminTree"
          :search="search"
          ref="treeview"
          activatable
          transition
          hoverable
          open-on-click
          return-object
        ></v-treeview>
      </v-card-text>
    </v-card>
  </div>
</template>
<script>
import groupHierarchyMixin from "../../../mixins/groupHierarchyMixin.js";
export default {
  mixins: [groupHierarchyMixin],
  data() {
    return {
      search: ""
    };
  },
  methods: {
    expandAll() {
      this.$refs["treeview"].updateAll(true);
    },
    closeAll() {
      this.$refs["treeview"].updateAll(false);
    }
  },
  computed: {},
  mounted() {
    console.log("treeview component mounted");
  }
};
</script>
