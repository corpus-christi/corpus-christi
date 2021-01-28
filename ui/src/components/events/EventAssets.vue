<template>
  <div>
    <v-card>
      <v-tabs vertical>
        <v-tab>
          <v-icon left>smartphone</v-icon>
          {{ $t("assets.title") }}
        </v-tab>
        <v-tab>
          <v-icon left>devices_other</v-icon>
          {{ $t("collections.title") }}
        </v-tab>

        <v-tab-item>
          <v-card flat>
            <v-toolbar>
              <v-text-field
                v-model="assetSearch"
                append-icon="search"
                v-bind:label="$t('actions.search')"
                single-line
                hide-details
              ></v-text-field>
              <v-spacer></v-spacer>
              <v-btn
                @click="showNewAssetDialog"
                color="primary"
                raised
              >
                <v-icon dark left>add</v-icon>
                {{ $t("assets.new") }}
              </v-btn>
            </v-toolbar>
            <v-data-table
              :items="assets"
              :headers="assetHeaders"
              :search="assetSearch"
              :loading="assetTableLoading"
            >
              <template v-slot:item="props">
                <tr>
                  <td>{{ props.item.asset.description }}</td>
                  <td>
                    <v-tooltip bottom>
                      <template v-slot:activator="{ on }">
                        <span v-on="on">{{ props.item.asset.location.description }}</span>
                      </template>
                      <span>{{ props.item.asset.location.address.address }}</span>
                    </v-tooltip>
                  </td>
                  <td>
                    <v-tooltip bottom>
                      <template v-slot:activator="{ on }">
                        <v-btn
                          @click="showDeleteAssetDialog(props.item.asset.id)"
                          icon
                          outlined
                          small
                          color="primary"
                          v-on="on"
                        >
                          <v-icon small>delete</v-icon>
                        </v-btn>
                      </template>
                      <span>{{ $t("actions.tooltips.remove") }}</span>
                    </v-tooltip>
                  </td>
                </tr>
              </template>
            </v-data-table>
          </v-card>
        </v-tab-item>
        <v-tab-item>
          <!-- TODO
            Once collections are implemented, 
            add a data table for them under this tab here
          -->
        </v-tab-item>
      </v-tabs>
    </v-card>

    <!-- Add Asset Dialog -->
    <v-dialog v-model="addAssetDialog.show" max-width="350px">
      <v-card>
        <v-card-title primary-title>
          {{ $t("assets.new") }}
        </v-card-title>
        <v-card-text>
          <entity-search
            multiple
            asset
            :existingEntities="assets"
            v-model="addAssetDialog.newAssets"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn
            @click="closeNewAssetDialog"
            color="secondary"
            text
            data-cy=""
          >
            {{ $t("actions.cancel") }}
          </v-btn>
          <v-spacer/>
          <v-btn
            @click="addAssets"
            color="primary"
            raised
            data-cy="confirm-asset"
          >
            {{ $t("actions.confirm") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Asset Dialog -->
    <v-dialog v-model="deleteAssetDialog.show" max-width="350px">
      <v-card>
        <v-card-text>
          {{ $t("events.assets.confirm-remove") }}
        </v-card-text>
        <v-card-actions>
          <v-btn
            @click="closeDeleteAssetDialog"
            color="secondary"
            text
          >
            {{ $t("actions.cancel") }}
          </v-btn>
          <v-spacer />
          <v-btn
            @click="deleteAsset"
            color="primary"
            raised
            :loading="deleteAssetDialog.loading"
          >
            {{ $t("actions.confirm") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn text @click="snackbar.show = false">
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>
  </div>
</template>

<script>
  import EntitySearch from '../EntitySearch.vue';
  export default {
    name: "EventAssets",
    components: { "entity-search": EntitySearch },

    data() {
      return {
        assetSearch: "",
        collectionSearch: "",
        assetTableLoading: false,
        assets: [],
        addAssetDialog: {
          show: false,
          newAssets: [],
          loading: false,
        },
        deleteAssetDialog: {
          show: false,
          assetId: -1,
          loading: false,
        },

        snackbar: {
          show: false,
          text: "",
        },
      };
    },

    computed: {
      assetHeaders() {
        return [
          { 
            text: this.$t("assets.description"),
            value: "asset.description",
            width: "30%",
          },
          {
            text: this.$t("assets.location"),
            value: "asset.location",
            width: "55%",
          },
          { text: this.$t("actions.header"), sortable: false },
        ];
      },
    },

    methods: {
      showNewAssetDialog() {
        this.addAssetDialog.show = true;
      },

      closeNewAssetDialog() {
        this.addAssetDialog.show = false;
      },

      showDeleteAssetDialog(assetId) {
        this.deleteAssetDialog.show = true;
        this.deleteAssetDialog.assetId = assetId;
      },

      closeDeleteAssetDialog() {
        this.deleteAssetDialog.show = false;
        this.deleteAssetDialog.loading = false;
        this.deleteAssetDialog.assetId = -1;
      },

      addAssets() {
        this.addAssetDialog.loading = true;
        let promises = [];

        for (let asset of this.addAssetDialog.newAssets) {
          const idx = this.assets.findIndex(
            (ev_as) => ev_as.assetId === asset.id
          );
          if (idx === -1) {
            promises.push(this.addAsset(asset.id));
          }
        }

        Promise.all(promises)
          .then(() => {
            this.getAssets();
          })
          .catch((err) => {
            console.log(err);
            this.addAssetDialog.loading = false;

          });
      },

      addAsset(id) {
        const eventId = this.$route.params.event;
        return this.$http.post(`/api/v1/events/${eventId}/assets/${id}`, {
          confirmed: true,
        });
      },

      deleteAsset() {
        this.deleteAssetDialog.loading = true;
        const eventId = this.$route.params.event;
        const assetId = this.deleteAssetDialog.assetId;
        const idx = this.assets.findIndex((ev) => ev.asset.id === assetId);
        this.$http
          .delete(`/api/v1/events/${eventId}/assets/${assetId}`)
          .then(() => {
            this.closeDeleteAssetDialog();
            this.assets.splice(idx, 1);
          })
          .catch((err) => {
            console.log(err);
            this.closeDeleteAssetDialog();
          })
      },

      getAssets() {
        this.assetTableLoading = true;
        const id = this.$route.params.event;
        this.$http
          .get(`/api/v1/events/${id}?include_assets=1`)
          .then((resp) => {
            let event = resp.data;
            this.assets = event.assets;
            this.assetTableLoading = false;
            console.log(this.assets);
          });
      },
    },

    mounted: function () {
      this.getAssets();
    },
  }
</script>