<template>
  <div>
    <v-toolbar class="pa-1">
      <v-layout align-center justify-space-between fill-height>
        <v-flex md2>
          <v-toolbar-title>{{ $t("assets.title") }}</v-toolbar-title>
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
            v-on:click.stop="newAsset"
            data-cy="add-asset"
          >
            <v-icon dark left>add</v-icon>
            {{ $t("assets.new") }}
          </v-btn>
        </v-flex>
      </v-layout>
    </v-toolbar>

    <v-data-table
      :rows-per-page-items="rowsPerPageItem"
      :headers="headers"
      :items="visibleAssets"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td>{{ props.item.description }}</td>
        <td>{{ getDisplayLocation(props.item.location) }}</td>
        <td>
          <template v-if="props.item.active">
            <v-tooltip bottom v-if="props.item.active">
              <v-btn
                icon
                outline
                small
                color="primary"
                slot="activator"
                v-on:click="editAsset(props.item)"
                data-cy="edit-asset"
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
                :loading="props.item.unarchiving"
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

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false">
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>

    <!-- New/Edit dialog -->
    <v-dialog v-model="assetDialog.show" max-width="500px" persistent>
      <asset-form
        v-bind:editMode="assetDialog.editMode"
        v-bind:initialData="assetDialog.asset"
        v-bind:saveLoading="assetDialog.saveLoading"
        v-bind:addMoreLoading="assetDialog.addMoreLoading"
        v-on:addAnother="addAnother"
        v-on:save="save"
        v-on:cancel="cancelAsset"
      />
    </v-dialog>

    <!-- Archive dialog -->
    <v-dialog v-model="archiveDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{ $t("assets.confirm-archive") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelArchive"
            color="secondary"
            flat
            data-cy="cancel-archive"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="archiveAsset"
            color="primary"
            raised
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import AssetForm from "./AssetForm";
import { mapGetters } from "vuex";

export default {
  name: "AssetTable",
  components: { "asset-form": AssetForm },
  mounted() {
    this.tableLoading = true;
    this.$http.get("/api/v1/assets/?include_location=1").then(resp => {
      this.assets = resp.data;
      this.tableLoading = false;
      console.log(this.assets);
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
      tableLoading: true,
      assets: [],
      assetDialog: {
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        asset: {}
      },
      archiveDialog: {
        show: false,
        assetId: -1,
        loading: false
      },
      search: "",

      snackbar: {
        show: false,
        text: ""
      },
      viewStatus: "viewAll",

      windowSize: {
        x: 0,
        y: 0,
        screen
      },
      addMore: false
    };
  },
  computed: {
    headers() {
      return [
        {
          text: this.$t("assets.description"),
          value: "description",
          width: "45%"
        },
        {
          text: this.$t("assets.location"),
          value: "location_name",
          width: "30%"
        },
        { text: this.$t("actions.header"), sortable: false, width: "25%" }
      ];
    },

    viewOptions() {
      return [
        { text: this.$t("actions.view-active"), value: "viewActive" },
        { text: this.$t("actions.view-archived"), value: "viewArchived" },
        { text: this.$t("actions.view-all"), value: "viewAll" }
      ];
    },

    visibleAssets() {
      if (this.viewStatus == "viewActive") {
        return this.assets.filter(as => as.active);
      } else if (this.viewStatus == "viewArchived") {
        return this.assets.filter(as => !as.active);
      } else {
        return this.assets;
      }
    },

    ...mapGetters(["currentLanguageCode"])
  },
  methods: {
    activateAssetDialog(asset = {}, editMode = false) {
      this.assetDialog.editMode = editMode;
      this.assetDialog.asset = asset;
      this.assetDialog.show = true;
    },

    editAsset(asset) {
      this.activateAssetDialog({ ...asset }, true);
    },

    activateArchiveDialog(assetId) {
      this.archiveDialog.show = true;
      this.archiveDialog.assetId = assetId;
    },

    confirmArchive(asset) {
      this.activateArchiveDialog(asset.id);
    },

    duplicate(asset) {
      const copyAsset = JSON.parse(JSON.stringify(asset));
      delete copyAsset.id;
      this.activateAssetDialog(copyAsset);
    },

    archiveAsset() {
      this.archiveDialog.loading = true;
      const assetId = this.archiveDialog.assetId;
      const idx = this.assets.findIndex(as => as.id === assetId);
      this.$http
        .delete(`/api/v1/assets/${assetId}`)
        .then(resp => {
          console.log("ARCHIVE", resp);
          this.assets[idx].active = false;
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          this.showSnackbar(this.$t("assets.asset-archived"));
        })
        .catch(err => {
          console.error("ARCHIVE FALURE", err.response);
          this.archiveDialog.loading = false;
          this.archiveDialog.show = false;
          this.showSnackbar(this.$t("assets.error-archiving-asset"));
        });

      // this.archiveDialog.show = false;
    },

    unarchive(asset) {
      const idx = this.assets.findIndex(as => as.id === asset.id);
      const copyAsset = JSON.parse(JSON.stringify(asset));
      asset.unarchiving = true;
      copyAsset.active = true;
      const patchId = copyAsset.id;
      delete copyAsset.id;
      delete copyAsset.location; //Temporary delete
      this.$http
        .patch(`/api/v1/assets/${patchId}`, { active: true })
        .then(resp => {
          console.log("UNARCHIVED", resp);
          delete asset.unarchiving;
          Object.assign(this.assets[idx], resp.data);
          this.showSnackbar(this.$t("assets.asset-unarchived"));
        })
        .catch(err => {
          delete asset.unarchiving;
          console.error("UNARCHIVE FALURE", err.response);
          this.showSnackbar(this.$t("assets.error-unarchiving-asset"));
        });
    },

    cancelArchive() {
      this.archiveDialog.show = false;
    },

    newAsset() {
      this.activateAssetDialog();
    },

    addAnother(asset) {
      this.addMore = true;
      this.assetDialog.addMoreLoading = true;
      this.saveAsset(asset);
    },

    save(asset) {
      this.assetDialog.saveLoading = true;
      this.saveAsset(asset);
    },

    saveAsset(asset) {
      asset.location_id = asset.location.id;
      let newAsset = JSON.parse(JSON.stringify(asset));
      delete newAsset.location;
      delete newAsset.id;
      if (this.assetDialog.editMode) {
        const assetId = asset.id;
        const idx = this.assets.findIndex(as => as.id === asset.id);
        delete newAsset.id;
        delete newAsset.event_count;
        this.$http
          .patch(`/api/v1/assets/${assetId}?include_location=1`, newAsset)
          .then(resp => {
            console.log("EDITED", resp);
            Object.assign(this.assets[idx], resp.data);
            this.cancelAsset();
            this.showSnackbar(this.$t("assets.asset-edited"));
          })
          .catch(err => {
            console.error("PUT FALURE", err.response);
            this.assetDialog.saveLoading = false;
            this.showSnackbar(this.$t("assets.error-editing-asset"));
          });
      } else {
        console.log(newAsset);
        delete newAsset.event_count;
        this.$http
          .post("/api/v1/assets/?include_location=1", newAsset)
          .then(resp => {
            console.log("ADDED", resp);
            this.assets.push(resp.data);
            if (this.addMore) this.clearAsset();
            else this.cancelAsset();
            this.showSnackbar(this.$t("assets.asset-added"));
          })
          .catch(err => {
            console.error("POST FAILURE", err.response);
            this.assetDialog.saveLoading = false;
            this.assetDialog.addMoreLoading = false;
            this.showSnackbar(this.$t("assets.error-adding-asset"));
          });
      }
    },

    clearAsset() {
      this.addMore = false;
      this.assetDialog.saveLoading = false;
      this.assetDialog.addMoreLoading = false;
      this.assetDialog.asset = {};
    },

    cancelAsset() {
      this.addMore = false;
      this.assetDialog.show = false;
      this.assetDialog.saveLoading = false;
      this.assetDialog.addMoreLoading = false;
    },

    addAnotherAsset(asset) {
      this.assetDialog.addMoreLoading = true;
      asset.location_id = asset.location.id;
      let newAsset = JSON.parse(JSON.stringify(asset));
      delete newAsset.location;
      this.$http
        .post("/api/v1/assets/?include_location=1", newAsset)
        .then(resp => {
          console.log("ADDED", resp);
          this.assets.push(resp.data);
          this.assetDialog.show = false;
          this.assetDialog.saveLoading = false;
          this.showSnackbar(this.$t("assets.asset-added"));
        })
        .catch(err => {
          console.error("FAILURE", err.response);
          this.assetDialog.saveLoading = false;
          this.showSnackbar(this.$t("assets.error-adding-asset"));
        });
    },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },

    getDisplayLocation(location, length = 20) {
      if (location && location.description) {
        let name = location.description;
        if (name && name.length && name.length > 0) {
          if (name.length > length) {
            return `${name.substring(0, length - 3)}...`;
          }
          return name;
        }
      }
      return name;
    },

    onResize() {
      this.windowSize = { x: window.innerWidth, y: window.innerHeight };
      if (this.windowSize.x <= 960) {
        this.windowSize.small = true;
      } else {
        this.windowSize.small = false;
      }
    }
  }
};
</script>

<style scoped></style>
