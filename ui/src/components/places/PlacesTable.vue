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
            v-on:click.stop="newAsset"
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
      :items="visiblePlaces"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td>{{ props.item.name }}</td>
        <td>{{ getDisplayLocation(props.item.address) }}</td>
        <td>{{ props.item.latitude }}</td>
        <td>{{ props.item.longitude }}</td>
      </template>
    </v-data-table>
  </div>
</template>

<script>
export default {
  name: "PlacesTable.vue",

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
        { text: this.$t("places.address.latitude"), sortable: false },
        { text: this.$t("places.address.longitude"), sortable: false },

        { text: this.$t("actions.header"), sortable: false }
      ];
    },
    visiblePlaces() {
      return this.assets;
    }
  }
};
</script>

<style scoped></style>
