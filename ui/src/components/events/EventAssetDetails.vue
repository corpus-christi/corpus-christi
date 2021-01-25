<template>
  <div>
    <v-card class="ma-1">
      <template v-if="loaded">
        <v-container fill-height fluid>
          <v-flex xs9 sm9 align-end flexbox>
            <span class="headline">{{ $t("assets.title") }}</span>
          </v-flex>
          <v-layout xs3 sm3 align-end justify-end>
            <v-btn
              text
              color="primary"
              data-cy="add-asset-dialog"
              v-on:click="addAssetDialog.show = true"
            >
              <v-icon>add</v-icon>&nbsp;{{ $t("assets.new") }}
            </v-btn>
          </v-layout>
        </v-container>
        <v-list v-if="assets.length">
          <template v-for="asset in assets">
            <v-divider v-bind:key="'assetDivider' + asset.id"></v-divider>
            <v-list-item v-bind:key="asset.id">
              <v-list-item-content>
                <v-container fluid>
                  <v-layout row justify-space-between align-center>
                    <v-flex>{{ asset.description }}</v-flex>
                    <v-flex shrink>
                      <v-btn
                        icon
                        outlined
                        text
                        color="primary"
                        v-on:click="showDeleteAssetDialog(asset.id)"
                        :data-cy="'deleteAsset-' + asset.id"
                        ><v-icon>delete</v-icon>
                      </v-btn>
                    </v-flex>
                  </v-layout>
                </v-container>
              </v-list-item-content>
            </v-list-item>
          </template>
        </v-list>
        <div v-else class="text-xs-center pa-4">
          {{ $t("assets.none-assigned") }}
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
    <!-- Add Asset dialog -->
    <v-dialog v-model="addAssetDialog.show" persistent max-width="500px">
      <v-card>
        <v-card-title primary-title>
          <span class="headline">{{ $t("assets.new") }}</span>
        </v-card-title>
        <v-card-text>
          <!-- TODO: make multiple -->
          <entity-search
            data-cy="asset-entity-search"
            v-model="addAssetDialog.asset"
            :existing-entities="assets"
            asset
          ></entity-search>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="closeAddAssetDialog()"
            color="secondary"
            text
            :disabled="addAssetDialog.loading"
            data-cy="cancel-add"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer />
          <v-btn
            v-on:click="addAsset()"
            color="primary"
            raised
            :disabled="!addAssetDialog.asset"
            :loading="addAssetDialog.loading"
            data-cy="confirm-add"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- Delete Asset dialog -->
    <v-dialog v-model="deleteAssetDialog.show" max-width="350px">
      <v-card>
        <v-card-text>
          <span>{{ $t("assets.confirm-remove-from-event") }}</span>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="deleteAssetDialog.show = false"
            color="secondary"
            text
            :disabled="deleteAssetDialog.loading"
            data-cy="cancel-delete"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer />
          <v-btn
            v-on:click="deleteAsset()"
            color="primary"
            raised
            :loading="deleteAssetDialog.loading"
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
  name: "EventAssetDetails",
  components: {
    "entity-search": EntitySearch,
  },

  props: {
    assets: {
      required: true,
    },
    loaded: {
      type: Boolean,
      required: true,
    },
  },

  data() {
    return {
      addAssetDialog: {
        show: false,
        loading: false,
        asset: null,
      },

      deleteAssetDialog: {
        show: false,
        loading: false,
        assetId: -1,
      },
    };
  },

  methods: {
    closeAddAssetDialog() {
      this.addAssetDialog.loading = false;
      this.addAssetDialog.show = false;
      this.addAssetDialog.asset = null;
    },

    addAsset() {
      // Emit asset-added event
      this.addAssetDialog.loading = true;
      this.$emit("asset-added", { asset: this.addAssetDialog.asset });
      this.closeAddAssetDialog();
      this.addAssetDialog.loading = false;
    },

    deleteAsset() {
      let id =  this.deleteAssetDialog.assetId;
      this.deleteAssetDialog.loading = true;
      // Emit asset-deleted event
      this.$emit("asset-deleted", { assetId: id });
      this.deleteAssetDialog.show = false;
      this.deleteAssetDialog.loading = false;
      this.deleteAssetDialog.assetId = -1;
    },

    showDeleteAssetDialog(assetId) {
      this.deleteAssetDialog.assetId = assetId;
      this.deleteAssetDialog.show = true;
    },

    showSnackbar(message) {
      this.$emit("snackbar", message);
    },
  },
};
</script>
