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
      :headers="headers"
      :items="AddressesLocationsData()"
      :search="search"
      :expand.sync="expanded"
      item-key="id"
      show-expand
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <tr @click="props.expanded = !props.expanded">
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
        </tr>
      </template>
      <template slot="expand" slot-scope="props">
        <v-container class="grey lighten-3">
          <v-layout>
            <v-flex md2> {{ $t("places.location.location") }}: </v-flex>
            <v-flex>
              <v-chip v-for="l in props.item.locations" :key="l.id" small
                >{{ l.description }}
              </v-chip>
            </v-flex>
            <v-flex md2>
              <v-tooltip bottom>
                <v-btn
                  icon
                  outline
                  small
                  color="primary"
                  slot="activator"
                  v-on:click="editLocation({address_id: props.item.id, allLocations: props.item.locations, editMode: true})"
                  data-cy="edit-locations"
                  :disabled="!props.item.locations.length"
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
                  v-on:click="newLocation({address_id: props.item.id, allLocations: [], editMode: false})"
                  data-cy="add-location"
                >
                  <v-icon small>add</v-icon>
                </v-btn>
                <span>{{ $t("places.location.new") }}</span>
              </v-tooltip>
            </v-flex>
          </v-layout>
        </v-container>
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
          v-bind:initialData="placeDialog.places"
          v-bind:areas="areas"
          v-bind:countries="countries"
          v-on:cancel="cancelPlace"
          v-on:saved="refreshPlacesList"
          v-on:subFormSaved="refreshPlacesList"
        />
      </v-layout>
    </v-dialog>
    <v-dialog
      scrollable
      persistent
      v-model="locationDialog.show"
      max-width="1000px"
    >
      <v-layout column>
        <v-card>
          <v-layout align-center justify-center row fill-height>
            <v-card-title class="headline">
              {{ $t(locationDialog.title) }}
            </v-card-title>
          </v-layout>
        </v-card>
        <LocationsForm
          v-bind:initialData="locationDialog.locationsInfo"
          v-on:cancel="cancelLocation"
          v-on:saved="refreshPlacesList"
          v-on:subFormSaved="refreshPlacesList"
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
        <GoogleMap v-bind:markers="markers"></GoogleMap>
      </v-flex>
    </v-layout>
  </div>
</template>

<script>
import PlaceForm from "./PlacesForm";
import LocationsForm from "./LocationsForm";
import GoogleMap from "../../components/GoogleMap";
export default {
  name: "PlacesTable",
  components: { PlaceForm, LocationsForm, GoogleMap },
  props: {
    addresses: Array,
    areas: Array,
    locations: Array,
    countries: Array
  },

  data() {
    return {
      expanded: [],
      placeDialog: {
        title: "",
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        places: {}
      },
      locationDialog: {
        title: "",
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        locationsInfo: {}
      },
      search: "",
      groupLocations: [],
      opened: [],
    };
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
          value: "latitude",
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
    },
    markers() {
      return this.addresses.map(element => {
        return {
          position: {
            lat: element.latitude,
            lng: element.longitude
          },
          data: {
            name: element.name,
            address: element.address
          },
          opened: false
        };
      });
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
    },
    activateLocationDialog(locationInfo = {}, editMode = false) {
      this.locationDialog.title = editMode
        ? this.$t("places.edit")
        : this.$t("places.location.new");
      this.locationDialog.locationsInfo = locationInfo;
      this.locationDialog.show = true;
    },
    editLocation(location) {
      this.activateLocationDialog({ ...location }, true);
    },
    newLocation(location) {
      this.activateLocationDialog({ ...location }, false);
    },
    cancelLocation() {
      this.locationDialog.show = false;
    },
    AddressesLocationsData() {
      let c = [];
      for (let i = 0; i < this.addresses.length; i++) {
        c.push(this.addresses[i]);
        c[i]["locations"] = [];
        for (let j = 0; j < this.locations.length; j++)
          if (c[i].id === this.locations[j].address_id) {
            c[i].locations.push({
              id: this.locations[j].id,
              description: this.locations[j].description
            });
          }
      }
      return c;
    }
  }
};
</script>

<style scoped></style>
