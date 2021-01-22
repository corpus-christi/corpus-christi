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
            ref="addressTable"
          ></v-text-field>
        </v-flex>

        <v-flex md2>
          <v-btn color="primary" raised v-on:click.stop="activateFilterDialog">
            <v-icon dark left>sort</v-icon>
            {{ $t("places.address.filters.address_filters") }}
          </v-btn>
        </v-flex>
        <v-flex md3>
          <div data-cy="view-dropdown">
            <v-select
              hide-details
              solo
              single-line
              :items="viewOptions"
              v-model="viewStatus"
            ></v-select>
          </div>
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

    <!-- Table of existing places -->
    <v-data-table
      :headers="headers"
      :items="addressesToDisplay"
      :search="search"
      expand
      item-key="id"
      class="elevation-1"
      hide-default-footer
      @page-count="pageCount = $event"
      :page.sync="page"
    >
      <template v-slot:item="props">
        <tr>
          <td>{{ props.item.name }}</td>
          <td>{{ props.item.address }}</td>
          <td>{{ props.item.city }}</td>
          <td>{{ props.item.latitude }}</td>
          <td>{{ props.item.longitude }}</td>
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn
                icon
                outlined
                small
                color="primary"
                slot="activator"
                v-on:click="editPlace(props.item)"
                data-cy="edit-place"
                v-on="on"
              >
                <v-icon small>edit</v-icon>
              </v-btn>
            </template>
            <span>{{ $t("actions.edit") }}</span>
          </v-tooltip>
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn
                icon
                outlined
                small
                color="primary"
                slot="activator"
                v-on:click="duplicate(props.item)"
                data-cy="duplicate-place"
                v-on="on"
              >
                <v-icon small>filter_none</v-icon>
              </v-btn>
            </template>
            <span>{{ $t("actions.duplicate") }}</span>
          </v-tooltip>
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn
                v-if="props.item.active === true"
                icon
                outlined
                small
                color="primary"
                slot="activator"
                v-on:click="showConfirmDialog('deactivate', props.item)"
                data-cy="deactivate-person"
                v-on="on"
              >
                <v-icon small>archive</v-icon>
              </v-btn>
            </template>
            <span>{{ $t("actions.tooltips.archive") }}</span>
          </v-tooltip>
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn
                v-if="props.item.active === false"
                icon
                outlined
                small
                color="primary"
                slot="activator"
                v-on:click="showConfirmDialog('activate', props.item)"
                data-cy="reactivate-person"
                v-on="on"
              >
                <v-icon small>undo</v-icon>
              </v-btn>
            </template>
            <span>{{ $t("actions.tooltips.activate") }}</span>
          </v-tooltip>
          <!-- TODO what is suppsoed in the expand filed?  Functionality is missing       -->
          <td v-if="!props.expanded">
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-btn
                  icon
                  slot="activator"
                  @click="props.expanded = !props.expanded"
                  v-on="on"
                >
                  <v-icon medium>expand_more</v-icon>
                </v-btn>
              </template>
              <span>{{ $t("places.expand") }}</span>
            </v-tooltip>
          </td>
          <td v-else>
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-btn
                  icon
                  slot="activator"
                  @click="props.expanded = !props.expanded"
                  v-on="on"
                >
                  <v-icon medium>expand_less</v-icon>
                </v-btn>
              </template>
              <span>{{ $t("places.close") }}</span>
            </v-tooltip>
          </td>
        </tr>
      </template>
      <template slot="expand" slot-scope="props" class="grey lighten-3">
        <v-container class="grey lighten-3">
          <v-layout>
            <v-flex md2>{{ $t("places.location.location") }}: </v-flex>
            <v-flex>
              <v-chip
                v-for="l in locationsToDisplay(
                  'deactivate',
                  props.item.locations
                )"
                :key="l.value"
                small
                color="white"
                >{{ l.text }}
              </v-chip>
            </v-flex>
            <v-flex md2>
              <v-tooltip bottom>
                <v-btn
                  icon
                  outlined
                  small
                  color="primary"
                  slot="activator"
                  v-on:click="
                    editLocation({
                      address_id: props.item.id,
                      allLocations: props.item.locations,
                      editMode: true,
                    })
                  "
                  data-cy="edit-locations"
                  :disabled="!props.item.locations.length"
                >
                  <v-icon small>edit</v-icon>
                </v-btn>
                <span>{{ $t("places.edit") }}</span>
              </v-tooltip>
              <v-tooltip bottom>
                <v-btn
                  icon
                  outlined
                  small
                  color="primary"
                  slot="activator"
                  v-on:click="
                    newLocation({
                      address_id: props.item.id,
                      allLocations: [],
                      editMode: false,
                    })
                  "
                  data-cy="add-location"
                >
                  <v-icon small>add</v-icon>
                </v-btn>
                <span>{{ $t("places.location.new") }}</span>
              </v-tooltip>
              <v-tooltip bottom>
                <v-btn
                  icon
                  outlined
                  small
                  color="primary"
                  slot="activator"
                  data-cy="deactivate-person"
                  v-on:click="
                    showLocationConfirmDialog('deactivate', props.item)
                  "
                >
                  <v-icon small>archive</v-icon>
                </v-btn>
                <span>{{ $t("actions.tooltips.archive") }}</span>
              </v-tooltip>
              <v-tooltip bottom>
                <v-btn
                  icon
                  outlined
                  small
                  color="primary"
                  slot="activator"
                  data-cy="reactivate-person"
                  v-on:click="showLocationConfirmDialog('activate', props.item)"
                >
                  <v-icon small>undo</v-icon>
                </v-btn>
                <span>{{ $t("actions.tooltips.activate") }}</span>
              </v-tooltip>
            </v-flex>
          </v-layout>
        </v-container>
      </template>
    </v-data-table>
    <div class="text-center pt-2">
      <v-pagination v-model="page" :length="pageCount"></v-pagination>
    </div>

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

    <v-dialog persistent v-model="filterDialog" max-width="800px">
      <v-container grid-list-md>
        <v-layout column>
          <v-card>
            <v-layout align-center justify-center row fill-height>
              <v-card-title class="headline">
                {{ $t("places.address.filters.address_filters") }}
              </v-card-title>
            </v-layout>
          </v-card>
          <v-card>
            <v-card-text>
              <v-layout column>
                <div>{{ $t("places.address.filters.range") }}</div>
                <v-layout row>
                  <v-flex md6>
                    <v-text-field
                      name="startLatitude"
                      v-model="filters.startLatitude"
                      :label="$t('places.address.filters.startLat')"
                    />
                  </v-flex>

                  <v-flex md6>
                    <v-text-field
                      name="endLatitude"
                      v-model="filters.endLatitude"
                      :label="$t('places.address.filters.endLat')"
                    />
                  </v-flex>
                </v-layout>

                <v-layout row>
                  <v-flex md6>
                    <v-text-field
                      name="startLongitude"
                      v-model="filters.startLongitude"
                      :label="$t('places.address.filters.startLng')"
                    />
                  </v-flex>
                  <v-flex md6>
                    <v-text-field
                      name="endLongitude"
                      v-model="filters.endLongitude"
                      :label="$t('places.address.filters.endLng')"
                    />
                  </v-flex>
                </v-layout>
                <v-divider></v-divider>
                <div>{{ $t("places.address.filters.distance-ll") }}</div>
                <v-layout row>
                  <v-flex md6>
                    <v-text-field
                      name="specificLatitude"
                      v-model="filters.specificLatitude"
                      :label="$t('places.address.latitude')"
                    />
                  </v-flex>

                  <v-flex md6>
                    <v-text-field
                      name="specificLongitude"
                      v-model="filters.specificLongitude"
                      :label="$t('places.address.longitude')"
                    />
                  </v-flex>
                </v-layout>

                <v-layout row>
                  <v-flex>
                    <v-text-field
                      name="distance"
                      v-model="filters.distance"
                      :label="$t('places.address.filters.distanceFromLatLng')"
                    />
                  </v-flex>
                </v-layout>
                <v-divider></v-divider>
                <div>{{ $t("places.address.filters.distance-addr") }}</div>
                <v-layout row>
                  <v-flex md6>
                    <v-autocomplete
                      name="addressDropdown"
                      :label="$t('places.address.address')"
                      v-model="filters.address"
                      :items="dropdownList"
                    />
                  </v-flex>

                  <v-flex md6>
                    <v-text-field
                      name="addressDistance"
                      v-model="filters.addressDistance"
                      :label="$t('places.address.filters.distanceFromAddress')"
                    />
                  </v-flex>
                </v-layout>
              </v-layout>
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn text color="primary" @click="resetFilters">
                {{ $t("places.address.filters.reset-filters") }}</v-btn
              >
              <v-btn text color="secondary" @click="cancelFilterDialog">{{
                $t("actions.cancel")
              }}</v-btn>
              <v-btn text color="primary" @click="applyFilters">
                {{ $t("places.address.filters.apply") }}</v-btn
              >
            </v-card-actions>
          </v-card>
        </v-layout>
      </v-container>
    </v-dialog>
    <v-layout class="mt-3">
      <v-flex>
        <v-toolbar color="blue" dark>
          <v-toolbar-title data-cy="church-sentence">
            {{ $t("places.address.address") }}
          </v-toolbar-title>
        </v-toolbar>
        <GoogleMap v-bind:markers="markers" />
      </v-flex>
    </v-layout>
    <v-dialog
      v-model="confirmDialog.show"
      max-width="350px"
      data-cy="place-table-confirmation"
    >
      <v-card>
        <v-card-text>{{ $t(confirmDialog.title) }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelAction"
            color="secondary"
            flat
            :disabled="confirmDialog.loading"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer />
          <v-btn
            v-on:click="
              confirmAction(confirmDialog.action, confirmDialog.place)
            "
            color="primary"
            raised
            :disabled="confirmDialog.loading"
            :loading="confirmDialog.loading"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="confirmLocationDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{ $t(confirmLocationDialog.title) }}</v-card-text>
        <v-autocomplete
          name="location"
          hide-details
          solo
          single-line
          :label="$t('places.location.location')"
          :items="
            locationsToDisplay(
              confirmLocationDialog.action,
              confirmLocationDialog.locationInfo.allLocations
            )
          "
          v-model="confirmLocationDialog.selectedLocation"
          v-validate="'required'"
          :error-messages="errors.collect('location')"
        />
        <v-card-actions>
          <v-btn
            v-on:click="cancelAction"
            color="secondary"
            flat
            :disabled="confirmLocationDialog.loading"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer />
          <v-btn
            v-on:click="
              confirmActionLocation(
                confirmLocationDialog.action,
                confirmLocationDialog.selectedLocation
              )
            "
            color="primary"
            raised
            :disabled="confirmLocationDialog.loading"
            :loading="confirmLocationDialog.loading"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import PlaceForm from "./PlacesForm";
import LocationsForm from "./LocationsForm";
import GoogleMap from "../../components/GoogleMap";
import { isEmpty } from "lodash";

export default {
  name: "PlacesTable",
  components: { PlaceForm, LocationsForm, GoogleMap },
  props: {
    addresses: Array,
    areas: Array,
    locations: Array,
    countries: Array,
  },
  data() {
    return {
      expanded: [],

      page: 1,
      pageCount: 0,

      placeDialog: {
        title: "",
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        places: {},
      },
      locationDialog: {
        title: "",
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        locationsInfo: {},
      },
      filters: {
        startLatitude: "",
        endLatitude: "",
        startLongitude: "",
        endLongitude: "",
        specificLatitude: "",
        specificLongitude: "",
        distance: "",
        addressDistance: "",
        address: {},
      },
      confirmDialog: {
        show: false,
        action: "",
        place: {},
        title: "",
        loading: false,
      },
      confirmLocationDialog: {
        show: false,
        action: "",
        locationInfo: {
          address_id: 0,
          allLocations: [],
        },
        selectedLocation: 0,
      },
      search: "",
      groupLocations: [],
      opened: [],
      filterDialog: false,
      viewStatus: "viewActive",
      allAddresses: [],
      activeAddresses: [],
      archivedAddresses: [],
    };
  },
  computed: {
    headers() {
      return [
        {
          text: this.$t("places.address.name"),
          value: "name",
          width: "20%",
        },
        {
          text: this.$t("places.address.address"),
          value: "address",
          width: "25%",
        },
        {
          text: this.$t("places.address.city"),
          value: "city",
          width: "20%",
        },
        {
          text: this.$t("places.address.latitude"),
          width: "6%",
          value: "latitude",
        },
        {
          text: this.$t("places.address.longitude"),
          width: "6%",
          value: "longitude",
        },
        { text: this.$t("actions.header"), width: "5%", sortable: false },
        { text: "", width: "5%", sortable: false },
      ];
    },
    visiblePlaces() {
      return this.assets;
    },
    viewOptions() {
      return [
        {
          text: this.$t("actions.view-active"),
          value: "viewActive",
          class: "view-active",
        },
        {
          text: this.$t("actions.view-archived"),
          value: "viewArchived",
          class: "view-archived",
        },
        { text: this.$t("actions.view-all"), value: "viewAll" },
      ];
    },
    addressesToDisplay() {
      switch (this.viewStatus) {
        case "viewActive":
          return this.activeAddresses;
        case "viewArchived":
          return this.archivedAddresses;
        case "viewAll":
          return this.allAddresses;
        default:
          return this.activeAddresses;
      }
    },
    markers() {
      return this.addressesToDisplay.map((element) => {
        return {
          position: {
            lat: element.latitude,
            lng: element.longitude,
          },
          data: {
            name: element.name,
            address: element.address,
          },
          opened: false,
        };
      });
    },
    dropdownList() {
      return this.addresses.map((element) => {
        return {
          text: element.address,
          value: element,
        };
      });
    },
  },
  watch: {
    addresses(all_addresses) {
      this.makeAddressLists(all_addresses);
    },
    locations() {
      this.makeAddressLists(this.addresses);
    },
  },
  methods: {
    duplicate(item) {
      console.log(item);
      //ToDo--  This functionality is missing
    },
    activatePlaceDialog(places = {}, editMode = false) {
      this.placeDialog.title = editMode
        ? this.$t("places.edit")
        : this.$t("places.new");
      this.placeDialog.places = places;
      this.placeDialog.show = true;
    },
    activateFilterDialog() {
      this.filterDialog = true;
    },
    isFilterEmpty() {
      return (
        this.filters.startLatitude === "" &&
        this.filters.endLatitude === "" &&
        this.filters.startLongitude === "" &&
        this.filters.endLongitude === "" &&
        this.filters.specificLatitude === "" &&
        this.filters.specificLongitude === "" &&
        this.filters.distance === "" &&
        this.filters.addressDistance === "" &&
        isEmpty(this.filters.address)
      );
    },
    resetFilters() {
      this.filters.startLatitude = "";
      this.filters.endLatitude = "";
      this.filters.startLongitude = "";
      this.filters.endLongitude = "";
      this.filters.specificLatitude = "";
      this.filters.specificLongitude = "";
      this.filters.distance = "";
      this.filters.addressDistance = "";
      this.filters.address = {};
      this.applyFilters();
    },
    applyFilters() {
      // console.log(this.filters);
      if (this.isFilterEmpty()) {
        this.$emit("fetchPlacesList");
      } else {
        // console.log(parseFloat(this.filters.startLongitude));
        // console.log(parseFloat(this.filters.endLongitude));
        // console.log(parseFloat(this.filters.startLatitude));
        // console.log(parseFloat(this.filters.endLatitude));
        this.$emit("fetchPlacesList", this.filters);
      }
      this.filterDialog = false;
    },
    editPlace(place) {
      this.activatePlaceDialog({ ...place }, true);
    },
    newPlace() {
      this.activatePlaceDialog();
    },
    cancelFilterDialog() {
      this.filterDialog = false;
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
    makeAddressLists(all_addresses) {
      this.allAddresses = this.AddressesLocationsData(all_addresses);
      this.activeAddresses = this.AddressesLocationsData(
        this.allAddresses.filter((person) => person.active)
      );
      this.archivedAddresses = this.AddressesLocationsData(
        this.allAddresses.filter((person) => !person.active)
      );
    },
    AddressesLocationsData(addArr) {
      let c = [];
      for (let i = 0; i < addArr.length; i++) {
        c.push(addArr[i]);
        c[i]["locations"] = [];
        for (let j = 0; j < this.locations.length; j++)
          if (c[i].id === this.locations[j].address_id) {
            c[i].locations.push({
              id: this.locations[j].id,
              description: this.locations[j].description,
              active: this.locations[j].active,
            });
          }
      }
      return c;
    },
    locationsToDisplay(action, locationsList) {
      if (action === "deactivate") {
        return locationsList
          .filter((location) => location.active)
          .map((element) => {
            return {
              text: this.$t(element.description),
              value: element.id,
            };
          });
      } else {
        return locationsList
          .filter((location) => !location.active)
          .map((element) => {
            return {
              text: this.$t(element.description),
              value: element.id,
            };
          });
      }
    },
    showConfirmDialog(action, place) {
      this.confirmDialog.title = "places.messages.confirm." + action;
      this.confirmDialog.action = action;
      this.confirmDialog.place = place;
      this.confirmDialog.show = true;
    },
    showLocationConfirmDialog(action, place) {
      this.confirmLocationDialog.title = "places.messages.confirm." + action;
      this.confirmLocationDialog.action = action;
      this.confirmLocationDialog.selectedLocation = 0;
      this.confirmLocationDialog.locationInfo = {
        address_id: place.id,
        allLocations: place.locations,
      };
      this.confirmLocationDialog.show = true;
    },
    confirmAction(action, place) {
      if (action === "deactivate") {
        this.deactivateAddress(place);
      } else if (action === "activate") {
        this.activateAddress(place);
      }
    },
    confirmActionLocation(action, location) {
      if (action === "deactivate") {
        this.deactivateLocation(location);
      } else if (action === "activate") {
        this.activateLocation(location);
      }
    },
    cancelAction() {
      this.confirmDialog.show = false;
      this.confirmLocationDialog.show = false;
    },
    deactivateAddress(place) {
      this.$http
        .patch(`/api/v1/places/addresses/${place.id}`, { active: false })
        .then((resp) => {
          console.log("DEACTIVATED ADDRESS", resp);
        })
        .then(() => {
          this.refreshPlacesList();
        })
        .then(() => {
          for (let loc = 0; loc < place.locations.length; loc++) {
            if (place.locations[loc].active) {
              this.deactivateLocation(place.locations[loc].id);
            }
          }
        })
        .catch((err) => {
          console.log("FAILED", err);
        })
        .finally(() => {
          this.confirmDialog.loading = false;
          this.confirmDialog.show = false;
        });
    },
    activateAddress(place) {
      this.$http
        .patch(`/api/v1/places/addresses/${place.id}`, { active: true })
        .then((resp) => {
          console.log("ACTIVATED ADDRESS", resp);
        })
        .then(() => {
          this.refreshPlacesList();
        })
        .catch((err) => {
          console.log("FAILED", err);
        })
        .finally(() => {
          this.confirmDialog.loading = false;
          this.confirmDialog.show = false;
        });
    },
    deactivateLocation(location) {
      this.$http
        .patch(`/api/v1/places/locations/${location}`, { active: false })
        .then((resp) => {
          console.log("DEACTIVATED LOCATION", resp);
        })
        .then(() => {
          this.refreshPlacesList();
        })
        .catch((err) => {
          console.log("FAILED", err);
        })
        .finally(() => {
          this.confirmLocationDialog.loading = false;
          this.confirmLocationDialog.show = false;
        });
    },
    activateLocation(location) {
      this.$http
        .patch(`/api/v1/places/locations/${location}`, { active: true })
        .then((resp) => {
          console.log("ACTIVATED LOCATION", resp);
        })
        .then(() => {
          this.refreshPlacesList();
        })
        .catch((err) => {
          console.log("FAILED", err);
        })
        .finally(() => {
          this.confirmLocationDialog.loading = false;
          this.confirmLocationDialog.show = false;
        });
    },
  },
};
</script>
