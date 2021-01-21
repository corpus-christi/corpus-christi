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
  </div>
</template>

<script>
  export default {
    name: "EventAssets",

    data() {
      return {
        assetSearch: "",
        collectionSearch: "",
        tableLoading: false,
        assets: [],
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
            width: "50%",
          },
          { text: this.$t("actions.header"), sortable: false },
        ];
      },
    },

    methods: {
        getAssets() {
          this.tableLoading = true;
          const id = this.$route.params.event;
          this.$http
            .get(`/api/v1/events/${id}?include_assets=1`)
            .then((resp) => {
              console.log("fetching...");
              console.log("resp: " + resp);
              let event = resp.data;
              this.assets = event.assets;
              this.tableLoading = false;
              console.log(this.assets);
            })
        }
    },

    mounted: function () {
      this.getAssets();
    },
  }
</script>