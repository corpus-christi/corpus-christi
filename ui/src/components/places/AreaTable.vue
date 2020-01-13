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
      :items="areas"
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
    locations: Array
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
      search: "",
      homegroups: [],
      groupLocations: []
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
    }
  }
};
</script>

<style scoped></style>
