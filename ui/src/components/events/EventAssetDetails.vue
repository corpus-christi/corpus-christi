<template>
  <div>
    <v-card class="ma-1">
      <template v-if="loaded">
        <v-container fill-height fluid>
          <v-col cols="9" sm="9" class="align-end">
            <span class="headline">{{ t("assets.title") }}</span>
          </v-col>
          <v-row cols="3" sm="3" align="end" justify="end">
            <v-btn
              variant="text"
              color="primary"
              data-cy="add-asset-dialog"
              v-on:click="addAssetDialog.show = true"
            >
              <v-icon>add</v-icon>&nbsp;{{ t("assets.new") }}
            </v-btn>
          </v-row>
        </v-container>
        <v-list v-if="assets.length">
          <template v-for="asset in assets" :key="'assetDivider' + asset.id">
            <v-divider></v-divider>
            <v-list-item>
              <v-container fluid class="pa-0">
                <v-row justify="space-between" align="center">
                  <v-col>{{ asset.description }}</v-col>
                  <v-col cols="auto">
                    <v-btn
                      icon
                      variant="outlined"
                      color="primary"
                      v-on:click="showDeleteAssetDialog(asset.id)"
                      :data-cy="'deleteAsset-' + asset.id"
                      ><v-icon>delete</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>
            </v-list-item>
          </template>
        </v-list>
        <div v-else class="text-center pa-4">
          {{ t("assets.none-assigned") }}
        </div>
      </template>
      <v-row v-else justify="center" style="height: 500px;">
        <div class="ma-5 pa-5">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>
      </v-row>
    </v-card>
    <!-- Add Asset dialog -->
    <v-dialog v-model="addAssetDialog.show" persistent max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">{{ t("assets.new") }}</span>
        </v-card-title>
        <v-card-text>
          <EntitySearch
            data-cy="asset-entity-search"
            v-model="addAssetDialog.asset"
            :existing-entities="assets"
            asset
          ></EntitySearch>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="closeAddAssetDialog()"
            color="secondary"
            variant="text"
            :disabled="addAssetDialog.loading"
            data-cy="cancel-add"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="addAsset()"
            color="primary"
            :disabled="!addAssetDialog.asset"
            :loading="addAssetDialog.loading"
            data-cy="confirm-add"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- Delete Asset dialog -->
    <v-dialog v-model="deleteAssetDialog.show" max-width="350px">
      <v-card>
        <v-card-text>
          <span>{{ t("assets.confirm-remove-from-event") }}</span>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="deleteAssetDialog.show = false"
            color="secondary"
            variant="text"
            :disabled="deleteAssetDialog.loading"
            data-cy="cancel-delete"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deleteAsset()"
            color="primary"
            :loading="deleteAssetDialog.loading"
            data-cy="confirm-delete"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import EntitySearch from "../EntitySearch.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const route = useRoute();

const props = defineProps<{
  assets: any[];
  loaded: boolean;
}>();

const emit = defineEmits(["snackbar", "asset-added"]);

const addAssetDialog = ref({ show: false, loading: false, asset: null as any });
const deleteAssetDialog = ref({ show: false, loading: false, assetId: -1 });

function closeAddAssetDialog() {
  addAssetDialog.value.loading = false;
  addAssetDialog.value.show = false;
  addAssetDialog.value.asset = null;
}

function addAsset() {
  const eventId = route.params.event;
  let assetId = addAssetDialog.value.asset.id;
  const idx = props.assets.findIndex(a => a.id === assetId);
  addAssetDialog.value.loading = true;
  if (idx > -1) {
    closeAddAssetDialog();
    emit("snackbar", t("assets.asset-on-event"));
    return;
  }

  http
    .post(`/api/v1/events/${eventId}/assets/${assetId}`)
    .then(() => {
      emit("snackbar", t("assets.asset-added"));
      closeAddAssetDialog();
      emit("asset-added");
    })
    .catch(err => {
      console.log(err);
      addAssetDialog.value.loading = false;
      if (err.response.status == 422) {
        emit("snackbar", t("assets.error-asset-assigned"));
      } else {
        emit("snackbar", t("assets.error-adding-asset"));
      }
    });
}

function deleteAsset() {
  let id = deleteAssetDialog.value.assetId;
  const idx = props.assets.findIndex(a => a.id === id);
  deleteAssetDialog.value.loading = true;
  const eventId = route.params.event;
  http
    .delete(`/api/v1/events/${eventId}/assets/${id}`)
    .then(resp => {
      console.log("REMOVED", resp);
      deleteAssetDialog.value.show = false;
      deleteAssetDialog.value.loading = false;
      deleteAssetDialog.value.assetId = -1;
      props.assets.splice(idx, 1);
      emit("snackbar", t("assets.asset-removed"));
    })
    .catch(err => {
      console.log(err);
      deleteAssetDialog.value.loading = false;
      emit("snackbar", t("assets.error-removing-asset"));
    });
}

function showDeleteAssetDialog(assetId: number) {
  deleteAssetDialog.value.assetId = assetId;
  deleteAssetDialog.value.show = true;
}
</script>
