<template>
  <div>
    <v-toolbar class="pa-1" data-cy="roles-toolbar">
      <v-layout align-center justify-space-between fill-height>
        <v-flex md2>
          <v-toolbar-title>{{ $t("places.location.location") }}</v-toolbar-title>
        </v-flex>
<!--        <v-flex md3>-->
<!--          <v-text-field-->
<!--            v-model="search"-->
<!--            append-icon="search"-->
<!--            v-bind:label="$t('actions.search')"-->
<!--            hide-details-->
<!--            clearable-->
<!--            single-line-->
<!--            box-->
<!--            data-cy="roles-search"-->
<!--          ></v-text-field>-->
<!--        </v-flex>-->
<!--        <v-flex md3>-->
<!--          <div data-cy="roles-dropdown">-->
<!--            <v-select-->
<!--              hide-details-->
<!--              solo-->
<!--              single-line-->
<!--              :label="$t('people.title-roles')"-->
<!--              :items="translatedRoles"-->
<!--            ></v-select>-->
<!--          </div>-->
<!--        </v-flex>-->
      </v-layout>
    </v-toolbar>

    <v-data-table
      :rows-per-page-items="rowsPerPageItem"
      :headers="headers"
      :items="locations"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">

        <td>{{ props.item.address.name }}</td>
        <td>{{ props.item.address.address }}</td>
        <td>{{ props.item.address.city }}</td>
        <td>{{ props.item.address.latitude }}</td>
        <td>{{ props.item.address.longitude }}</td>
        <td>{{  props.item.description }}
<!--          <v-chip v-for="location in props.item.description" small-->
<!--            >{{location}}</v-chip-->
<!--          >-->
        </td>

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
      </template>
    </v-data-table>
  </div>
</template>

<script>
import PlaceForm from "./PlacesForm";
import GoogleMap from "../../components/GoogleMap";
export default {
  name: "LocationsTable",
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
          value: "name"
        },
        {
          text: this.$t("places.address.address"),
          value: "address"
        },
        {
          text: this.$t("places.address.city"),
          value: "city"
        },
        {
          text: this.$t("places.address.latitude"),
          value: "latitude"
        },
        {
          text: this.$t("places.address.longitude"),
          value: "longitude"
        },
        {
          text: this.$t("places.location.location"),
          value: "locations"
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
    }
  }
};
</script>

<style scoped>

</style>
