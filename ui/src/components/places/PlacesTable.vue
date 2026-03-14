<template>
  <div>
    <v-toolbar class="pa-1">
      <v-row align="center" justify="space-between">
        <v-col md="2">
          <v-toolbar-title>{{ t("places.address.address") }}</v-toolbar-title>
        </v-col>
        <v-col md="2">
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="t('actions.search')"
            single-line
            hide-details
            data-cy="form-search"
            ref="addressTable"
          ></v-text-field>
        </v-col>

        <v-col md="2">
          <v-btn color="primary" variant="elevated" v-on:click.stop="activateFilterDialog">
            <v-icon dark left>sort</v-icon>
            {{ t("places.address.filters.address_filters") }}
          </v-btn>
        </v-col>
        <v-col md="3">
          <div data-cy="view-dropdown">
            <v-select
              hide-details
              solo
              single-line
              :items="viewOptions"
              v-model="viewStatus"
            ></v-select>
          </div>
        </v-col>
        <v-col shrink>
          <v-btn
            color="primary"
            variant="elevated"
            v-on:click.stop="newPlace"
            data-cy="add-place"
          >
            <v-icon dark left>add</v-icon>
            {{ t("places.address.new") }}
          </v-btn>
        </v-col>
      </v-row>
    </v-toolbar>

    <v-data-table
      :headers="headers"
      :items="addressesToDisplay"
      :search="search"
      item-key="id"
      class="elevation-1"
    >
      <template #item="{ item }">
        <tr>
          <td>{{ item.name }}</td>
          <td>{{ item.address }}</td>
          <td>{{ item.city }}</td>
          <td>{{ item.latitude }}</td>
          <td>{{ item.longitude }}</td>
          <td>
            <v-tooltip bottom>
              <template #activator="{ props: tooltipProps }">
                <v-btn
                  icon
                  variant="outlined"
                  size="small"
                  color="primary"
                  v-bind="tooltipProps"
                  v-on:click="editPlace(item)"
                  data-cy="edit-place"
                >
                  <v-icon size="small">edit</v-icon>
                </v-btn>
              </template>
              <span>{{ t("actions.edit") }}</span>
            </v-tooltip>
            <v-tooltip bottom>
              <template #activator="{ props: tooltipProps }">
                <v-btn
                  icon
                  variant="outlined"
                  size="small"
                  color="primary"
                  v-bind="tooltipProps"
                  v-on:click="duplicate(item)"
                  data-cy="duplicate-place"
                >
                  <v-icon size="small">filter_none</v-icon>
                </v-btn>
              </template>
              <span>{{ t("actions.duplicate") }}</span>
            </v-tooltip>
            <v-tooltip bottom v-if="item.active === true">
              <template #activator="{ props: tooltipProps }">
                <v-btn
                  icon
                  variant="outlined"
                  size="small"
                  color="primary"
                  v-bind="tooltipProps"
                  v-on:click="showConfirmDialog('deactivate', item)"
                  data-cy="deactivate-person"
                >
                  <v-icon size="small">archive</v-icon>
                </v-btn>
              </template>
              <span>{{ t("actions.tooltips.archive") }}</span>
            </v-tooltip>
            <v-tooltip bottom v-if="item.active === false">
              <template #activator="{ props: tooltipProps }">
                <v-btn
                  icon
                  variant="outlined"
                  size="small"
                  color="primary"
                  v-bind="tooltipProps"
                  v-on:click="showConfirmDialog('activate', item)"
                  data-cy="reactivate-person"
                >
                  <v-icon size="small">undo</v-icon>
                </v-btn>
              </template>
              <span>{{ t("actions.tooltips.activate") }}</span>
            </v-tooltip>
          </td>
          <td>
            <v-tooltip bottom>
              <template #activator="{ props: tooltipProps }">
                <v-btn
                  icon
                  variant="text"
                  v-bind="tooltipProps"
                  @click="toggleExpand(item)"
                >
                  <v-icon>{{ expandedItems.includes(item.id) ? 'expand_less' : 'expand_more' }}</v-icon>
                </v-btn>
              </template>
              <span>{{ expandedItems.includes(item.id) ? t("places.close") : t("places.expand") }}</span>
            </v-tooltip>
          </td>
        </tr>
        <tr v-if="expandedItems.includes(item.id)">
          <td colspan="7" class="grey lighten-3">
            <v-container class="grey lighten-3">
              <v-row>
                <v-col md="2">{{ t("places.location.location") }}: </v-col>
                <v-col>
                  <v-chip
                    v-for="l in locationsToDisplay('deactivate', item.locations)"
                    :key="l.value"
                    size="small"
                    color="white"
                    >{{ l.title }}
                  </v-chip>
                </v-col>
                <v-col md="2">
                  <v-tooltip bottom>
                    <template #activator="{ props: tooltipProps }">
                      <v-btn
                        icon
                        variant="outlined"
                        size="small"
                        color="primary"
                        v-bind="tooltipProps"
                        v-on:click="editLocation({ address_id: item.id, allLocations: item.locations, editMode: true })"
                        data-cy="edit-locations"
                        :disabled="!item.locations.length"
                      >
                        <v-icon size="small">edit</v-icon>
                      </v-btn>
                    </template>
                    <span>{{ t("places.edit") }}</span>
                  </v-tooltip>
                  <v-tooltip bottom>
                    <template #activator="{ props: tooltipProps }">
                      <v-btn
                        icon
                        variant="outlined"
                        size="small"
                        color="primary"
                        v-bind="tooltipProps"
                        v-on:click="newLocation({ address_id: item.id, allLocations: [], editMode: false })"
                        data-cy="add-location"
                      >
                        <v-icon size="small">add</v-icon>
                      </v-btn>
                    </template>
                    <span>{{ t("places.location.new") }}</span>
                  </v-tooltip>
                  <v-tooltip bottom>
                    <template #activator="{ props: tooltipProps }">
                      <v-btn
                        icon
                        variant="outlined"
                        size="small"
                        color="primary"
                        v-bind="tooltipProps"
                        data-cy="deactivate-person"
                        v-on:click="showLocationConfirmDialog('deactivate', item)"
                      >
                        <v-icon size="small">archive</v-icon>
                      </v-btn>
                    </template>
                    <span>{{ t("actions.tooltips.archive") }}</span>
                  </v-tooltip>
                  <v-tooltip bottom>
                    <template #activator="{ props: tooltipProps }">
                      <v-btn
                        icon
                        variant="outlined"
                        size="small"
                        color="primary"
                        v-bind="tooltipProps"
                        data-cy="reactivate-person"
                        v-on:click="showLocationConfirmDialog('activate', item)"
                      >
                        <v-icon size="small">undo</v-icon>
                      </v-btn>
                    </template>
                    <span>{{ t("actions.tooltips.activate") }}</span>
                  </v-tooltip>
                </v-col>
              </v-row>
            </v-container>
          </td>
        </tr>
      </template>
    </v-data-table>
    <v-dialog
      scrollable
      persistent
      v-model="placeDialog.show"
      max-width="1000px"
    >
      <v-col>
        <v-card>
          <v-row align="center" justify="center">
            <v-card-title class="headline">
              {{ t(placeDialog.title) }}
            </v-card-title>
          </v-row>
        </v-card>
        <PlaceForm
          v-bind:initialData="placeDialog.places"
          v-bind:areas="areas"
          v-bind:countries="countries"
          v-on:cancel="cancelPlace"
          v-on:saved="refreshPlacesList"
          v-on:subFormSaved="refreshPlacesList"
        />
      </v-col>
    </v-dialog>
    <v-dialog
      scrollable
      persistent
      v-model="locationDialog.show"
      max-width="1000px"
    >
      <v-col>
        <v-card>
          <v-row align="center" justify="center">
            <v-card-title class="headline">
              {{ t(locationDialog.title) }}
            </v-card-title>
          </v-row>
        </v-card>
        <LocationsForm
          v-bind:initialData="locationDialog.locationsInfo"
          v-on:cancel="cancelLocation"
          v-on:saved="refreshPlacesList"
          v-on:subFormSaved="refreshPlacesList"
        />
      </v-col>
    </v-dialog>

    <v-dialog persistent v-model="filterDialog" max-width="800px">
      <v-container>
        <v-col>
          <v-card>
            <v-row align="center" justify="center">
              <v-card-title class="headline">
                {{ t("places.address.filters.address_filters") }}
              </v-card-title>
            </v-row>
          </v-card>
          <v-card>
            <v-card-text>
              <v-col>
                <div>{{ t("places.address.filters.range") }}</div>
                <v-row>
                  <v-col md="6">
                    <v-text-field
                      name="startLatitude"
                      v-model="filters.startLatitude"
                      :label="t('places.address.filters.startLat')"
                    ></v-text-field>
                  </v-col>

                  <v-col md="6">
                    <v-text-field
                      name="endLatitude"
                      v-model="filters.endLatitude"
                      :label="t('places.address.filters.endLat')"
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col md="6">
                    <v-text-field
                      name="startLongitude"
                      v-model="filters.startLongitude"
                      :label="t('places.address.filters.startLng')"
                    ></v-text-field>
                  </v-col>
                  <v-col md="6">
                    <v-text-field
                      name="endLongitude"
                      v-model="filters.endLongitude"
                      :label="t('places.address.filters.endLng')"
                    ></v-text-field>
                  </v-col>
                </v-row>
                <v-divider></v-divider>
                <div>{{ t("places.address.filters.distance-ll") }}</div>
                <v-row>
                  <v-col md="6">
                    <v-text-field
                      name="specificLatitude"
                      v-model="filters.specificLatitude"
                      :label="t('places.address.latitude')"
                    ></v-text-field>
                  </v-col>

                  <v-col md="6">
                    <v-text-field
                      name="specificLongitude"
                      v-model="filters.specificLongitude"
                      :label="t('places.address.longitude')"
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col>
                    <v-text-field
                      name="distance"
                      v-model="filters.distance"
                      :label="t('places.address.filters.distanceFromLatLng')"
                    ></v-text-field>
                  </v-col>
                </v-row>
                <v-divider></v-divider>
                <div>{{ t("places.address.filters.distance-addr") }}</div>
                <v-row>
                  <v-col md="6">
                    <v-autocomplete
                      name="addressDropdown"
                      :label="t('places.address.address')"
                      v-model="filters.address"
                      :items="dropdownList"
                    ></v-autocomplete>
                  </v-col>

                  <v-col md="6">
                    <v-text-field
                      name="addressDistance"
                      v-model="filters.addressDistance"
                      :label="t('places.address.filters.distanceFromAddress')"
                    ></v-text-field>
                  </v-col>
                </v-row>
              </v-col>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn variant="text" color="secondary" @click="cancelFilterDialog">{{
                t("actions.cancel")
              }}</v-btn>

              <v-btn variant="text" color="primary" @click="applyFilters">{{
                t("places.address.filters.apply")
              }}</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-container>
    </v-dialog>
    <v-row class="mt-3">
      <v-col>
        <v-toolbar color="blue" dark>
          <v-toolbar-title data-cy="church-sentence">
            {{ t("places.address.address") }}
          </v-toolbar-title>
        </v-toolbar>
        <GoogleMap v-bind:markers="markers" />
      </v-col>
    </v-row>
    <v-dialog
      v-model="confirmDialog.show"
      max-width="350px"
      data-cy="place-table-confirmation"
    >
      <v-card>
        <v-card-text>{{ t(confirmDialog.title) }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelAction"
            color="secondary"
            variant="text"
            :disabled="confirmDialog.loading"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="confirmAction(confirmDialog.action, confirmDialog.place)"
            color="primary"
            variant="elevated"
            :disabled="confirmDialog.loading"
            :loading="confirmDialog.loading"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="confirmLocationDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{ t(confirmLocationDialog.title) }}</v-card-text>
        <v-autocomplete
          name="location"
          hide-details
          solo
          single-line
          :label="t('places.location.location')"
          :items="locationsToDisplay(confirmLocationDialog.action, confirmLocationDialog.locationInfo.allLocations)"
          v-model="confirmLocationDialog.selectedLocation"
        ></v-autocomplete>
        <v-card-actions>
          <v-btn
            v-on:click="cancelAction"
            color="secondary"
            variant="text"
            :disabled="confirmLocationDialog.loading"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="confirmActionLocation(confirmLocationDialog.action, confirmLocationDialog.selectedLocation)"
            color="primary"
            variant="elevated"
            :disabled="confirmLocationDialog.loading"
            :loading="confirmLocationDialog.loading"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import { isEmpty } from "lodash";
import PlaceForm from "./PlacesForm.vue";
import LocationsForm from "./LocationsForm.vue";
import GoogleMap from "../../components/GoogleMap.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;

const props = defineProps<{
  addresses?: any[];
  areas?: any[];
  locations?: any[];
  countries?: any[];
}>();

const emit = defineEmits(["fetchPlacesList"]);

const expandedItems = ref<number[]>([]);
const placeDialog = ref({
  title: "",
  show: false,
  editMode: false,
  saveLoading: false,
  addMoreLoading: false,
  places: {} as any
});

const locationDialog = ref({
  title: "",
  show: false,
  editMode: false,
  saveLoading: false,
  addMoreLoading: false,
  locationsInfo: {} as any
});

const filters = ref({
  startLatitude: "",
  endLatitude: "",
  startLongitude: "",
  endLongitude: "",
  specificLatitude: "",
  specificLongitude: "",
  distance: "",
  addressDistance: "",
  address: {} as any
});

const confirmDialog = ref({
  show: false,
  action: "",
  place: {} as any,
  title: "",
  loading: false
});

const confirmLocationDialog = ref({
  show: false,
  action: "",
  title: "",
  locationInfo: {
    address_id: 0,
    allLocations: [] as any[]
  },
  selectedLocation: 0,
  loading: false
});

const search = ref("");
const filterDialog = ref(false);
const viewStatus = ref("viewActive");
const allAddresses = ref<any[]>([]);
const activeAddresses = ref<any[]>([]);
const archivedAddresses = ref<any[]>([]);

const headers = computed(() => [
  { title: t("places.address.name"), value: "name", width: "20%" },
  { title: t("places.address.address"), value: "address", width: "25%" },
  { title: t("places.address.city"), value: "city", width: "20%" },
  { title: t("places.address.latitude"), width: "6%", value: "latitude" },
  { title: t("places.address.longitude"), width: "6%", value: "longitude" },
  { title: t("actions.header"), width: "5%", sortable: false },
  { title: "", width: "5%", sortable: false }
]);

const viewOptions = computed(() => [
  { title: t("actions.view-active"), value: "viewActive", class: "view-active" },
  { title: t("actions.view-archived"), value: "viewArchived", class: "view-archived" },
  { title: t("actions.view-all"), value: "viewAll" }
]);

const addressesToDisplay = computed(() => {
  switch (viewStatus.value) {
    case "viewActive":
      return activeAddresses.value;
    case "viewArchived":
      return archivedAddresses.value;
    case "viewAll":
      return allAddresses.value;
    default:
      return activeAddresses.value;
  }
});

const markers = computed(() => {
  return addressesToDisplay.value.map(element => ({
    position: {
      lat: element.latitude,
      lng: element.longitude
    },
    data: {
      name: element.name,
      address: element.address
    },
    opened: false
  }));
});

const dropdownList = computed(() => {
  if (!props.addresses) return [];
  return props.addresses.map(element => ({
    title: element.address,
    value: element
  }));
});

watch(
  () => props.addresses,
  (all_addresses) => {
    if (all_addresses) {
      makeAddressLists(all_addresses);
    }
  }
);

watch(
  () => props.locations,
  () => {
    if (props.addresses) {
      makeAddressLists(props.addresses);
    }
  }
);

function toggleExpand(item: any) {
  const idx = expandedItems.value.indexOf(item.id);
  if (idx >= 0) {
    expandedItems.value.splice(idx, 1);
  } else {
    expandedItems.value.push(item.id);
  }
}

function makeAddressLists(all_addresses: any[]) {
  allAddresses.value = addressesLocationsData(all_addresses);
  activeAddresses.value = addressesLocationsData(allAddresses.value.filter(a => a.active));
  archivedAddresses.value = addressesLocationsData(allAddresses.value.filter(a => !a.active));
}

function addressesLocationsData(addArr: any[]) {
  let c: any[] = [];
  for (let i = 0; i < addArr.length; i++) {
    c.push({ ...addArr[i] });
    c[i]["locations"] = [];
    if (props.locations) {
      for (let j = 0; j < props.locations.length; j++) {
        if (c[i].id === props.locations[j].address_id) {
          c[i].locations.push({
            id: props.locations[j].id,
            description: props.locations[j].description,
            active: props.locations[j].active
          });
        }
      }
    }
  }
  return c;
}

function locationsToDisplay(action: string, locationsList: any[]) {
  if (!locationsList) return [];
  if (action === "deactivate") {
    return locationsList
      .filter(location => location.active)
      .map(element => ({
        title: t(element.description),
        value: element.id
      }));
  } else {
    return locationsList
      .filter(location => !location.active)
      .map(element => ({
        title: t(element.description),
        value: element.id
      }));
  }
}

function activatePlaceDialog(places: any = {}, editMode = false) {
  placeDialog.value.title = editMode ? t("places.edit") : t("places.new");
  placeDialog.value.places = places;
  placeDialog.value.show = true;
}

function activateFilterDialog() {
  filterDialog.value = true;
}

function isFilterEmpty() {
  return (
    filters.value.startLatitude === "" &&
    filters.value.endLatitude === "" &&
    filters.value.startLongitude === "" &&
    filters.value.endLongitude === "" &&
    filters.value.specificLatitude === "" &&
    filters.value.specificLongitude === "" &&
    filters.value.distance === "" &&
    filters.value.addressDistance === "" &&
    isEmpty(filters.value.address)
  );
}

function applyFilters() {
  if (isFilterEmpty()) {
    emit("fetchPlacesList");
  } else {
    emit("fetchPlacesList", filters.value);
  }
  filterDialog.value = false;
}

function editPlace(place: any) {
  activatePlaceDialog({ ...place }, true);
}

function duplicate(place: any) {
  const copyPlace = JSON.parse(JSON.stringify(place));
  delete copyPlace.id;
  activatePlaceDialog(copyPlace);
}

function newPlace() {
  activatePlaceDialog();
}

function cancelFilterDialog() {
  filterDialog.value = false;
}

function cancelPlace() {
  placeDialog.value.show = false;
}

function refreshPlacesList() {
  emit("fetchPlacesList");
}

function activateLocationDialog(locationInfo: any = {}, editMode = false) {
  locationDialog.value.title = editMode ? t("places.edit") : t("places.location.new");
  locationDialog.value.locationsInfo = locationInfo;
  locationDialog.value.show = true;
}

function editLocation(location: any) {
  activateLocationDialog({ ...location }, true);
}

function newLocation(location: any) {
  activateLocationDialog({ ...location }, false);
}

function cancelLocation() {
  locationDialog.value.show = false;
}

function showConfirmDialog(action: string, place: any) {
  confirmDialog.value.title = "places.messages.confirm." + action;
  confirmDialog.value.action = action;
  confirmDialog.value.place = place;
  confirmDialog.value.show = true;
}

function showLocationConfirmDialog(action: string, place: any) {
  confirmLocationDialog.value.title = "places.messages.confirm." + action;
  confirmLocationDialog.value.action = action;
  confirmLocationDialog.value.selectedLocation = 0;
  confirmLocationDialog.value.locationInfo = {
    address_id: place.id,
    allLocations: place.locations
  };
  confirmLocationDialog.value.show = true;
}

function confirmAction(action: string, place: any) {
  if (action === "deactivate") {
    deactivateAddress(place);
  } else if (action === "activate") {
    activateAddress(place);
  }
}

function confirmActionLocation(action: string, location: number) {
  if (action === "deactivate") {
    deactivateLocation(location);
  } else if (action === "activate") {
    activateLocation(location);
  }
}

function cancelAction() {
  confirmDialog.value.show = false;
  confirmLocationDialog.value.show = false;
}

function deactivateAddress(place: any) {
  http
    .patch(`/api/v1/places/addresses/${place.id}`, { active: false })
    .then(resp => {
      console.log("DEACTIVATED ADDRESS", resp);
    })
    .then(() => {
      refreshPlacesList();
    })
    .then(() => {
      for (let loc = 0; loc < place.locations.length; loc++) {
        if (place.locations[loc].active) {
          deactivateLocation(place.locations[loc].id);
        }
      }
    })
    .catch(err => {
      console.log("FAILED", err);
    })
    .finally(() => {
      confirmDialog.value.loading = false;
      confirmDialog.value.show = false;
    });
}

function activateAddress(place: any) {
  http
    .patch(`/api/v1/places/addresses/${place.id}`, { active: true })
    .then(resp => {
      console.log("ACTIVATED ADDRESS", resp);
    })
    .then(() => {
      refreshPlacesList();
    })
    .catch(err => {
      console.log("FAILED", err);
    })
    .finally(() => {
      confirmDialog.value.loading = false;
      confirmDialog.value.show = false;
    });
}

function deactivateLocation(location: number) {
  http
    .patch(`/api/v1/places/locations/${location}`, { active: false })
    .then(resp => {
      console.log("DEACTIVATED LOCATION", resp);
    })
    .then(() => {
      refreshPlacesList();
    })
    .catch(err => {
      console.log("FAILED", err);
    })
    .finally(() => {
      confirmLocationDialog.value.loading = false;
      confirmLocationDialog.value.show = false;
    });
}

function activateLocation(location: number) {
  http
    .patch(`/api/v1/places/locations/${location}`, { active: true })
    .then(resp => {
      console.log("ACTIVATED LOCATION", resp);
    })
    .then(() => {
      refreshPlacesList();
    })
    .catch(err => {
      console.log("FAILED", err);
    })
    .finally(() => {
      confirmLocationDialog.value.loading = false;
      confirmLocationDialog.value.show = false;
    });
}
</script>
