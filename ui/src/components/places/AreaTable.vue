<template>
  <div>
    <v-toolbar class="pa-1">
      <v-layout align-center justify-space-between fill-height>
        <v-flex md2>
          <v-toolbar-title>{{ $t("places.area.area") }}</v-toolbar-title>
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
            v-on:click.stop="newArea"
            data-cy="add-area"
          >
            <v-icon dark left>add</v-icon>
            {{ $t("places.area.new") }}
          </v-btn>
        </v-flex>
      </v-layout>
    </v-toolbar>

    <v-data-table
      :headers="headers"
      :items="areasToDisplay"
      :search="search"
      class="elevation-1"
    >
      <template slot="items" slot-scope="props">
        <td>{{ props.item.name }}</td>
        <td>{{ $t(props.item.country.name_i18n) }}</td>

        <v-tooltip bottom>
          <v-btn
            icon
            outline
            small
            color="primary"
            slot="activator"
            v-on:click="editArea(props.item)"
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

        <v-tooltip bottom>
          <v-btn
            v-if="props.item.active === true"
            icon
            outline
            small
            color="primary"
            slot="activator"
            v-on:click="showConfirmDialog('deactivate', props.item)"
            data-cy="deactivate-area"
          >
            <v-icon small>archive</v-icon>
          </v-btn>
          <span>{{ $t("actions.tooltips.archive") }}</span>
        </v-tooltip>
        <v-tooltip bottom>
          <v-btn
            v-if="props.item.active === false"
            icon
            outline
            small
            color="primary"
            slot="activator"
            v-on:click="showConfirmDialog('activate', props.item)"
            data-cy="reactivate-area"
          >
            <v-icon small>undo</v-icon>
          </v-btn>
          <span>{{ $t("actions.tooltips.activate") }}</span>
        </v-tooltip>
      </template>
    </v-data-table>

    <v-dialog
      scrollable
      persistent
      v-model="areaDialog.show"
      max-width="1000px"
    >
      <v-layout column>
        <v-card>
          <v-layout align-center justify-center row fill-height>
            <v-card-title class="headline">
              {{ $t(areaDialog.title) }}
            </v-card-title>
          </v-layout>
        </v-card>
        <AreaForm
          v-bind:countries="countries"
          v-on:cancel="cancelArea"
          v-on:saved="refreshPlacesList"
          v-bind:initialData="areaDialog.area"
        />
      </v-layout>
    </v-dialog>
    <v-layout class="mt-3">
      <v-flex>
        <v-toolbar color="blue" dark>
          <v-toolbar-title data-cy="church-sentence">
            {{ $t("places.area.area") }}
          </v-toolbar-title>
        </v-toolbar>
        <GoogleMap v-bind:markers="homegroups"></GoogleMap>
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
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="
              confirmAction(confirmDialog.action, confirmDialog.area)
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
  </div>
</template>

<script>
import AreaForm from "./AreaForm";
import GoogleMap from "../../components/GoogleMap";
export default {
  name: "AreaTable",
  components: { AreaForm, GoogleMap },
  props: {
    addresses: Array,
    areas: Array,
    locations: Array,
    countries: Array
  },

  data() {
    return {
      areaDialog: {
        title: "",
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        area: {}
      },
      confirmDialog: {
        show: false,
        action: "",
        area: {},
        title: "",
        loading: false
      },
      search: "",
      homegroups: [],
      groupLocations: [],
      viewStatus: "viewActive",
      allAreas: [],
      activeAreas: [],
      archivedAreas: []
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
          text: this.$t("places.address.country"),
          value: "country",
          width: "20%"
        },

        { text: this.$t("actions.header"), width: "17%", sortable: false }
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
          class: "view-active"
        },
        {
          text: this.$t("actions.view-archived"),
          value: "viewArchived",
          class: "view-archived"
        },
        { text: this.$t("actions.view-all"), value: "viewAll" }
      ];
    },
    areasToDisplay() {
      switch (this.viewStatus) {
        case "viewActive":
          return this.activeAreas;
        case "viewArchived":
          return this.archivedAreas;
        case "viewAll":
          return this.allAreas;
        default:
          return this.activeAreas;
      }
    }
  },
  watch: {
    areas(all_areas) {
      this.allAreas = all_areas;
      this.activeAreas = this.allAreas.filter(area => area.active);
      this.archivedAreas = this.allAreas.filter(area => !area.active);
    }
  },
  methods: {
    activateAreaDialog(area = {}, editMode = false) {
      this.areaDialog.title = editMode
        ? this.$t("places.area.edit")
        : this.$t("places.area.new");
      this.areaDialog.area = {
        id: area.id,
        name: area.name,
        country_code: area.country_code
      };
      this.areaDialog.show = true;
    },

    editArea(area) {
      this.activateAreaDialog({ ...area }, true);
    },

    newArea() {
      this.activateAreaDialog();
    },

    cancelArea() {
      this.areaDialog.show = false;
    },

    refreshPlacesList() {
      this.$emit("fetchPlacesList");
    },
    showConfirmDialog(action, area) {
      this.confirmDialog.title = "places.area.confirm." + action;
      this.confirmDialog.action = action;
      this.confirmDialog.area = area;
      this.confirmDialog.show = true;
    },
    confirmAction(action, area) {
      if (action === "deactivate") {
        this.deactivateArea(area);
      } else if (action === "activate") {
        this.activateArea(area);
      }
    },
    cancelAction() {
      this.confirmDialog.show = false;
    },
    deactivateArea(area) {
      console.log(area);
      this.$http
        .patch(`/api/v1/places/areas/${area.id}`, { active: false })
        .then(resp => {
          console.log("DEACTIVATED AREA", resp);
        })
        .then(() => {
          this.refreshPlacesList();
        })
        .catch(err => {
          console.log("FAILED", err);
        })
        .finally(() => {
          this.confirmDialog.loading = false;
          this.confirmDialog.show = false;
        });
    },
    activateArea(area) {
      console.log(area);
      this.$http
        .patch(`/api/v1/places/areas/${area.id}`, { active: true })
        .then(resp => {
          console.log("ACTIVATED AREA", resp);
        })
        .then(() => {
          this.refreshPlacesList();
        })
        .catch(err => {
          console.log("FAILED", err);
        })
        .finally(() => {
          this.confirmDialog.loading = false;
          this.confirmDialog.show = false;
        });
    }
  }
};
</script>

<style scoped></style>
