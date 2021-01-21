<template>
  <div>
    <v-card>
      <v-tabs vertical>
        <v-tab>
          <v-icon left>smartphone</v-icon>
          Assets
        </v-tab>
        <v-tab>
          <v-icon left>devices_other</v-icon>
          Collections
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
                Add Asset
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
          hi
        </v-tab-item>
      </v-tabs>
    </v-card>

    <!-- Add Asset Dialog -->
    <v-dialog v-model="addAssetDialog.show" max-width="350px">
      <v-card>
        <v-card-title primary-title>
          Add Participant
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
            Cancel
          </v-btn>
          <v-spacer/>
          <v-btn
            color="primary"
            raised
            data-cy="confirm-asset"
          >
            Confirm
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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
      }
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
        console.log("assets: " + this.assets);
        console.log(this.assets);
        this.addAssetDialog.show = true;
      },

      closeNewAssetDialog() {
        this.addAssetDialog.show = false;
      },

      addAssets() {

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
          })
      }
    },

    mounted: function () {
      this.getAssets();
    },
  }
</script>