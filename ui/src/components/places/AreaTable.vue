<template>
  <div>
    <v-toolbar class="pa-1">
      <v-row align="center" justify="space-between">
        <v-col md="2">
          <v-toolbar-title>{{ t("places.area.area") }}</v-toolbar-title>
        </v-col>
        <v-col md="2">
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="t('actions.search')"
            single-line
            hide-details
            data-cy="form-search"
          ></v-text-field>
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
            v-on:click.stop="newArea"
            data-cy="add-area"
          >
            <v-icon dark left>add</v-icon>
            {{ t("places.area.new") }}
          </v-btn>
        </v-col>
      </v-row>
    </v-toolbar>

    <v-data-table
      :headers="headers"
      :items="areasToDisplay"
      :search="search"
      class="elevation-1"
    >
      <template #item="{ item }">
        <tr>
          <td>{{ item.name }}</td>
          <td>{{ t(item.country.name_i18n) }}</td>
          <td>
            <v-tooltip bottom>
              <template #activator="{ props: tooltipProps }">
                <v-btn
                  icon
                  variant="outlined"
                  size="small"
                  color="primary"
                  v-bind="tooltipProps"
                  v-on:click="editArea(item)"
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

            <v-tooltip bottom>
              <template #activator="{ props: tooltipProps }">
                <v-btn
                  v-if="item.active === true"
                  icon
                  variant="outlined"
                  size="small"
                  color="primary"
                  v-bind="tooltipProps"
                  v-on:click="showConfirmDialog('deactivate', item)"
                  data-cy="deactivate-area"
                >
                  <v-icon size="small">archive</v-icon>
                </v-btn>
              </template>
              <span>{{ t("actions.tooltips.archive") }}</span>
            </v-tooltip>
            <v-tooltip bottom>
              <template #activator="{ props: tooltipProps }">
                <v-btn
                  v-if="item.active === false"
                  icon
                  variant="outlined"
                  size="small"
                  color="primary"
                  v-bind="tooltipProps"
                  v-on:click="showConfirmDialog('activate', item)"
                  data-cy="reactivate-area"
                >
                  <v-icon size="small">undo</v-icon>
                </v-btn>
              </template>
              <span>{{ t("actions.tooltips.activate") }}</span>
            </v-tooltip>
          </td>
        </tr>
      </template>
    </v-data-table>

    <v-dialog
      scrollable
      persistent
      v-model="areaDialog.show"
      max-width="1000px"
    >
      <v-col>
        <v-card>
          <v-row align="center" justify="center">
            <v-card-title class="headline">
              {{ t(areaDialog.title) }}
            </v-card-title>
          </v-row>
        </v-card>
        <AreaForm
          v-bind:countries="countries"
          v-on:cancel="cancelArea"
          v-on:saved="refreshPlacesList"
          v-bind:initialData="areaDialog.area"
        />
      </v-col>
    </v-dialog>
    <v-row class="mt-3">
      <v-col>
        <v-toolbar color="blue" dark>
          <v-toolbar-title data-cy="church-sentence">
            {{ t("places.area.area") }}
          </v-toolbar-title>
        </v-toolbar>
        <GoogleMap v-bind:markers="homegroups"></GoogleMap>
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
            v-on:click="confirmAction(confirmDialog.action, confirmDialog.area)"
            color="primary"
            variant="elevated"
            :disabled="confirmDialog.loading"
            :loading="confirmDialog.loading"
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
import AreaForm from "./AreaForm.vue";
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

const areaDialog = ref({
  title: "",
  show: false,
  editMode: false,
  saveLoading: false,
  addMoreLoading: false,
  area: {} as any
});

const confirmDialog = ref({
  show: false,
  action: "",
  area: {} as any,
  title: "",
  loading: false
});

const search = ref("");
const homegroups = ref<any[]>([]);
const viewStatus = ref("viewActive");
const allAreas = ref<any[]>([]);
const activeAreas = ref<any[]>([]);
const archivedAreas = ref<any[]>([]);

const headers = computed(() => [
  { title: t("places.address.name"), value: "name", width: "20%" },
  { title: t("places.address.country"), value: "country", width: "20%" },
  { title: t("actions.header"), width: "17%", sortable: false }
]);

const viewOptions = computed(() => [
  { title: t("actions.view-active"), value: "viewActive", class: "view-active" },
  { title: t("actions.view-archived"), value: "viewArchived", class: "view-archived" },
  { title: t("actions.view-all"), value: "viewAll" }
]);

const areasToDisplay = computed(() => {
  switch (viewStatus.value) {
    case "viewActive":
      return activeAreas.value;
    case "viewArchived":
      return archivedAreas.value;
    case "viewAll":
      return allAreas.value;
    default:
      return activeAreas.value;
  }
});

watch(
  () => props.areas,
  (all_areas) => {
    if (all_areas) {
      allAreas.value = all_areas;
      activeAreas.value = allAreas.value.filter((area: any) => area.active);
      archivedAreas.value = allAreas.value.filter((area: any) => !area.active);
    }
  }
);

function activateAreaDialog(area: any = {}, editMode = false) {
  areaDialog.value.title = editMode
    ? t("places.area.edit")
    : t("places.area.new");
  areaDialog.value.area = {
    id: area.id,
    name: area.name,
    country_code: area.country_code
  };
  areaDialog.value.show = true;
}

function editArea(area: any) {
  activateAreaDialog({ ...area }, true);
}

function newArea() {
  activateAreaDialog();
}

function cancelArea() {
  areaDialog.value.show = false;
}

function duplicate(area: any) {
  const copyArea = JSON.parse(JSON.stringify(area));
  delete copyArea.id;
  activateAreaDialog(copyArea);
}

function refreshPlacesList() {
  emit("fetchPlacesList");
}

function showConfirmDialog(action: string, area: any) {
  confirmDialog.value.title = "places.area.confirm." + action;
  confirmDialog.value.action = action;
  confirmDialog.value.area = area;
  confirmDialog.value.show = true;
}

function confirmAction(action: string, area: any) {
  if (action === "deactivate") {
    deactivateArea(area);
  } else if (action === "activate") {
    activateArea(area);
  }
}

function cancelAction() {
  confirmDialog.value.show = false;
}

function deactivateArea(area: any) {
  console.log(area);
  http
    .patch(`/api/v1/places/areas/${area.id}`, { active: false })
    .then(resp => {
      console.log("DEACTIVATED AREA", resp);
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

function activateArea(area: any) {
  console.log(area);
  http
    .patch(`/api/v1/places/areas/${area.id}`, { active: true })
    .then(resp => {
      console.log("ACTIVATED AREA", resp);
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
</script>

<style scoped></style>
