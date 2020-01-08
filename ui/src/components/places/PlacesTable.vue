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
      </template>
    </v-data-table>

    <v-dialog
      scrollable
      persistent
      v-model="placeDialog.show"
      max-width="1000px"
    >
      <v-layout column>
        <v-card>
          <v-layout align-center justify-center row fill-height>
            <v-card-title class="headline">
              {{ $t(placeDialog.title)}}
            </v-card-title>
          </v-layout>
        </v-card>
        <PlaceForm
          v-on:cancel="cancelPlace"
          v-on:saved="refreshPlacesList"
          v-bind:initialData="placeDialog.places"
        />
      </v-layout>
    </v-dialog>
  </div>
</template>

<script>
import PlaceForm from "./PlacesForm";
export default {
  name: "PlacesTable.vue",
    components: {PlaceForm},
    props: {
    addresses: Array,
    areas: Array,
    locations: Array
  },

  data() {
    return {
      placeDialog: {
        title: "",
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
    activatePlaceDialog(places = {}, editMode = false) {
      this.placeDialog.title = editMode
        ? this.$t("places.edit")
        : this.$t("places.new");
      this.placeDialog.places = places;
      this.placeDialog.show = true;
    },

    editPlace(place) {
      this.activatePlaceDialog({ ...place }, true);
    },

    newPlace() {
      this.activatePlaceDialog();
    },

    cancelPlace() {
      this.placeDialog.show = false;
    },

    refreshPlacesList() {
        this.$emit("fetchPlacesList");
    }
  }
};
</script>

<style scoped></style>
