<template>
  <div>
    <v-toolbar class="pa-1">
      <v-row align="center" justify="space-between" no-gutters>
        <v-col md="2">
          <v-toolbar-title>{{ t("assets.title") }}</v-toolbar-title>
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
          <v-select
            hide-details
            solo
            single-line
            :items="viewOptions"
            v-model="viewStatus"
            data-cy="view-status-select"
          >
          </v-select>
        </v-col>
        <v-col cols="auto" class="justify-self-end">
          <v-btn
            color="primary"
            v-on:click.stop="newAsset"
            data-cy="add-asset"
          >
            <v-icon dark start>add</v-icon>
            {{ t("assets.new") }}
          </v-btn>
        </v-col>
      </v-row>
    </v-toolbar>

    <v-data-table
      :headers="headers"
      :items="visibleAssets"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template #item="{ item }">
        <tr>
          <td>{{ item.description }}</td>
          <td>{{ getDisplayLocation(item.location) }}</td>
          <td>
            <template v-if="item.active">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <v-btn
                    icon
                    variant="outlined"
                    size="small"
                    color="primary"
                    v-bind="props"
                    v-on:click="editAsset(item)"
                    data-cy="edit-asset"
                  >
                    <v-icon size="small">edit</v-icon>
                  </v-btn>
                </template>
                <span>{{ t("actions.edit") }}</span>
              </v-tooltip>
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <v-btn
                    icon
                    variant="outlined"
                    size="small"
                    color="primary"
                    v-bind="props"
                    v-on:click="duplicate(item)"
                  >
                    <v-icon size="small">filter_none</v-icon>
                  </v-btn>
                </template>
                <span>{{ t("actions.duplicate") }}</span>
              </v-tooltip>
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <v-btn
                    icon
                    variant="outlined"
                    size="small"
                    color="primary"
                    v-bind="props"
                    v-on:click="confirmArchive(item)"
                    data-cy="archive"
                  >
                    <v-icon size="small">archive</v-icon>
                  </v-btn>
                </template>
                <span>{{ t("actions.tooltips.archive") }}</span>
              </v-tooltip>
            </template>
            <template v-else>
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <v-btn
                    icon
                    variant="outlined"
                    size="small"
                    color="primary"
                    v-bind="props"
                    v-on:click="unarchive(item)"
                    :loading="item.unarchiving"
                    data-cy="unarchive"
                  >
                    <v-icon size="small">undo</v-icon>
                  </v-btn>
                </template>
                <span>{{ t("actions.tooltips.activate") }}</span>
              </v-tooltip>
            </template>
          </td>
        </tr>
      </template>
    </v-data-table>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false">
          {{ t("actions.close") }}
        </v-btn>
      </template>
    </v-snackbar>

    <!-- New/Edit dialog -->
    <v-dialog v-model="assetDialog.show" max-width="500px" persistent>
      <AssetForm
        v-bind:editMode="assetDialog.editMode"
        v-bind:initialData="assetDialog.asset"
        v-bind:saveLoading="assetDialog.saveLoading"
        v-bind:addMoreLoading="assetDialog.addMoreLoading"
        v-on:addAnother="addAnother"
        v-on:save="save"
        v-on:cancel="cancelAsset"
      />
    </v-dialog>

    <!-- Archive dialog -->
    <v-dialog v-model="archiveDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{ t("assets.confirm-archive") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelArchive"
            color="secondary"
            variant="text"
            data-cy="cancel-archive"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="archiveAsset"
            color="primary"
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import AssetForm from "./AssetForm.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;

const tableLoading = ref(true);
const assets = ref<any[]>([]);
const assetDialog = ref({
  show: false,
  editMode: false,
  saveLoading: false,
  addMoreLoading: false,
  asset: {} as Record<string, any>
});
const archiveDialog = ref({
  show: false,
  assetId: -1,
  loading: false
});
const search = ref("");
const snackbar = ref({ show: false, text: "" });
const viewStatus = ref("viewAll");
const addMore = ref(false);

const headers = computed(() => [
  { title: t("assets.description"), value: "description", width: "45%" },
  { title: t("assets.location"), value: "location_name", width: "30%" },
  { title: t("actions.header"), sortable: false, width: "25%" }
]);

const viewOptions = computed(() => [
  { title: t("actions.view-active"), value: "viewActive" },
  { title: t("actions.view-archived"), value: "viewArchived" },
  { title: t("actions.view-all"), value: "viewAll" }
]);

const visibleAssets = computed(() => {
  if (viewStatus.value === "viewActive") return assets.value.filter(as => as.active);
  else if (viewStatus.value === "viewArchived") return assets.value.filter(as => !as.active);
  else return assets.value;
});

function activateAssetDialog(asset: Record<string, any> = {}, editMode = false) {
  assetDialog.value.editMode = editMode;
  assetDialog.value.asset = asset;
  assetDialog.value.show = true;
}

function editAsset(asset: any) {
  activateAssetDialog({ ...asset }, true);
}

function activateArchiveDialog(assetId: number) {
  archiveDialog.value.show = true;
  archiveDialog.value.assetId = assetId;
}

function confirmArchive(asset: any) {
  activateArchiveDialog(asset.id);
}

function duplicate(asset: any) {
  const copyAsset = JSON.parse(JSON.stringify(asset));
  delete copyAsset.id;
  activateAssetDialog(copyAsset);
}

function archiveAsset() {
  archiveDialog.value.loading = true;
  const assetId = archiveDialog.value.assetId;
  const idx = assets.value.findIndex(as => as.id === assetId);
  http
    .delete(`/api/v1/assets/${assetId}`)
    .then(resp => {
      console.log("ARCHIVE", resp);
      assets.value[idx].active = false;
      archiveDialog.value.loading = false;
      archiveDialog.value.show = false;
      showSnackbar(t("assets.asset-archived"));
    })
    .catch(err => {
      console.error("ARCHIVE FAILURE", err.response);
      archiveDialog.value.loading = false;
      archiveDialog.value.show = false;
      showSnackbar(t("assets.error-archiving-asset"));
    });
}

function unarchive(asset: any) {
  const idx = assets.value.findIndex(as => as.id === asset.id);
  const copyAsset = JSON.parse(JSON.stringify(asset));
  asset.unarchiving = true;
  copyAsset.active = true;
  const patchId = copyAsset.id;
  delete copyAsset.id;
  delete copyAsset.location;
  http
    .patch(`/api/v1/assets/${patchId}`, { active: true })
    .then(resp => {
      console.log("UNARCHIVED", resp);
      delete asset.unarchiving;
      Object.assign(assets.value[idx], resp.data);
      showSnackbar(t("assets.asset-unarchived"));
    })
    .catch(err => {
      delete asset.unarchiving;
      console.error("UNARCHIVE FAILURE", err.response);
      showSnackbar(t("assets.error-unarchiving-asset"));
    });
}

function cancelArchive() {
  archiveDialog.value.show = false;
}

function newAsset() {
  activateAssetDialog();
}

function addAnother(asset: any) {
  addMore.value = true;
  assetDialog.value.addMoreLoading = true;
  saveAsset(asset);
}

function save(asset: any) {
  assetDialog.value.saveLoading = true;
  saveAsset(asset);
}

function saveAsset(asset: any) {
  asset.location_id = asset.location.id;
  let newAsset = JSON.parse(JSON.stringify(asset));
  delete newAsset.location;
  delete newAsset.id;
  if (assetDialog.value.editMode) {
    const assetId = asset.id;
    const idx = assets.value.findIndex(as => as.id === asset.id);
    delete newAsset.id;
    delete newAsset.event_count;
    http
      .patch(`/api/v1/assets/${assetId}?include_location=1`, newAsset)
      .then(resp => {
        Object.assign(assets.value[idx], resp.data);
        cancelAsset();
        showSnackbar(t("assets.asset-edited"));
      })
      .catch(err => {
        console.error("PUT FAILURE", err.response);
        assetDialog.value.saveLoading = false;
        showSnackbar(t("assets.error-editing-asset"));
      });
  } else {
    delete newAsset.event_count;
    http
      .post("/api/v1/assets/?include_location=1", newAsset)
      .then(resp => {
        assets.value.push(resp.data);
        if (addMore.value) clearAsset();
        else cancelAsset();
        showSnackbar(t("assets.asset-added"));
      })
      .catch(err => {
        console.error("POST FAILURE", err.response);
        assetDialog.value.saveLoading = false;
        assetDialog.value.addMoreLoading = false;
        showSnackbar(t("assets.error-adding-asset"));
      });
  }
}

function clearAsset() {
  addMore.value = false;
  assetDialog.value.saveLoading = false;
  assetDialog.value.addMoreLoading = false;
  assetDialog.value.asset = {};
}

function cancelAsset() {
  addMore.value = false;
  assetDialog.value.show = false;
  assetDialog.value.saveLoading = false;
  assetDialog.value.addMoreLoading = false;
}

function showSnackbar(message: string) {
  snackbar.value.text = message;
  snackbar.value.show = true;
}

function getDisplayLocation(location: any, length = 20) {
  if (location && location.description) {
    let name = location.description;
    if (name && name.length && name.length > 0) {
      if (name.length > length) {
        return `${name.substring(0, length - 3)}...`;
      }
      return name;
    }
  }
  return "";
}

onMounted(() => {
  tableLoading.value = true;
  http.get("/api/v1/assets/?include_location=1").then(resp => {
    assets.value = resp.data;
    tableLoading.value = false;
  });
});
</script>

<style scoped></style>
