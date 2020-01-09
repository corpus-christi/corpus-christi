<template>
  <div>
    <v-toolbar class="pa-1">
      <v-layout align-center justify-space-between fill-height>
        <v-flex md2>
          <v-toolbar-title>{{ $t("places.address.address") }}</v-toolbar-title>
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

        <v-flex shrink justify-self-end>
          <v-btn
            color="primary"
            raised
            v-on:click.stop="newPlace"
            data-cy="add-place"
          >
            <v-icon dark left>add</v-icon>
            {{ $t("places.address.new") }}
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
        <td>{{ props.item.city }}</td>
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
              {{ $t(placeDialog.title) }}
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
    <v-layout class="mt-3">
      <v-flex>
        <v-toolbar color="blue" dark>
          <v-toolbar-title data-cy="church-sentence">
            {{ $t("places.address.address") }}
          </v-toolbar-title>
        </v-toolbar>
        <GoogleMap v-bind:markers="homegroups"></GoogleMap>
      </v-flex>
    </v-layout>
  </div>
</template>

<script>
import PlaceForm from "./PlacesForm";
import GoogleMap from "../../components/GoogleMap";
export default {
  name: "PlacesTable.vue",
  components: { PlaceForm, GoogleMap },
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
      },
      search: "",
      homegroups: [],
      groupLocations: []
    };
  },

  mounted() {
    this.getHomegroupLocations();
  },
  computed: {
    headers() {
      return [
        {
          text: this.$t("places.address.name"),
          value: "name",
          width: "20%"
        },
        {
          text: this.$t("places.address.address"),
          value: "address",
          width: "30%"
        },
        {
          text: this.$t("places.address.city"),
          value: "city",
          width: "20%"
        },
        {
          text: this.$t("places.address.latitude"),
          width: "4%",
          value: "latitude"
        },
        {
          text: this.$t("places.address.longitude"),
          width: "4%",
          value: "longitude"
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
