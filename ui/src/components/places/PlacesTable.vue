<template>
  <div>
    <v-toolbar class="pa-1">
      <v-layout align-center justify-space-between fill-height>
        <v-flex md2>
          <v-toolbar-title>{{ $t("places.title") }}</v-toolbar-title>
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
            v-on:click.stop="newPlace"
            data-cy="add-asset"
          >
            <v-icon dark left>add</v-icon>
            {{ $t("places.new") }}
          </v-btn>
        </v-flex>
      </v-layout>
    </v-toolbar>

    <v-data-table
      :rows-per-page-items="rowsPerPageItem"
      :headers="headers"
      :items="addresses"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td>{{ props.item.name }}</td>
        <td>{{ props.item.address }}</td>
        <td>{{ props.item.latitude }}</td>
        <td>{{ props.item.longitude }}</td>

        <v-tooltip bottom>
          <v-btn
            icon
            outline
            small
            color="primary"
            slot="activator"
            v-on:click="editPlace(props.item)"
            data-cy="edit-place"
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
            data-cy="duplicate-place"
          >
            <v-icon small>filter_none</v-icon>
          </v-btn>
          <span>{{ $t("actions.duplicate") }}</span>
        </v-tooltip>
      </template>
    </v-data-table>
  </div>
</template>

<script>
export default {
  name: "PlacesTable.vue",
  props: {
    addresses: Array,
    areas: Array,
    locations: Array
  },

  data() {
    return {
      placeDialog: {
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        places: {}
      }
    };
  },

  computed: {
    headers() {
      return [
        {
          text: this.$t("places.address.name"),
          value: name,
          // width: "17%",
          sortable: false
        },
        { text: this.$t("places.address.address"), sortable: false },
        {
          text: this.$t("places.address.latitude"),
          width: "4%",
          sortable: false
        },
        {
          text: this.$t("places.address.longitude"),
          width: "4%",
          sortable: false
        },

        { text: this.$t("actions.header"), width: "17%", sortable: false }
      ];
    },
    visiblePlaces() {
      return this.assets;
    }
  },
  methods: {
    activePlaceDialog(asset = {}, editMode = false) {
      this.placeDialog.editMode = editMode;
      this.placeDialog.asset = asset;
      this.placeDialog.show = true;
    },

    editPlace(place) {
      this.activatePlaceDialog({ ...place }, true);
    }
  }
};
</script>

<style scoped></style>
