<template>
  <div>
    <!-- Header -->
    <v-toolbar>
      <v-row align="center" justify="space-between" no-gutters>
        <v-col md="2">
          <v-toolbar-title>{{ t("diplomas.diplomas") }}</v-toolbar-title>
        </v-col>
        <v-spacer></v-spacer>
        <v-col md="3">
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="t('actions.search')"
            single-line
            hide-details
            data-cy="diplomas-table-search"
          ></v-text-field>
        </v-col>
        <v-spacer></v-spacer>
        <v-col md="3">
          <v-select
            v-model="viewStatus"
            :items="options"
            solo
            hide-details
            data-cy="diplomas-table-viewstatus"
          ></v-select>
        </v-col>

        <v-col cols="auto">
          <v-btn
            color="primary"
            v-on:click.stop="newDiploma"
            data-cy="diplomas-table-new"
          >
            <v-icon start>library_add</v-icon>
            {{ t("diplomas.new") }}
          </v-btn>
        </v-col>
      </v-row>
    </v-toolbar>

    <!-- Table of existing diplomas -->
    <v-data-table
      :headers="headers"
      :items="showDiplomas"
      :loading="!tableLoaded"
      :search="search"
      class="elevation-1"
      data-cy="diplomas-table"
    >
      <template #item="{ item }">
        <tr>
          <td class="hover-hand" @click="clickThrough(item)">
            {{ item.name }}
          </td>
          <td class="hover-hand" @click="clickThrough(item)">
            {{ item.description }}
          </td>
          <td class="hover-hand">
            <DiplomaAdminActions
              v-bind:diploma="item"
              display-context="compact"
              v-on:action="dispatchAction($event, item)"
            />
          </td>
        </tr>
      </template>
    </v-data-table>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false">{{
          t("actions.close")
        }}</v-btn>
      </template>
    </v-snackbar>

    <!-- New/Edit dialog -->
    <v-dialog v-model="diplomaDialog.show" max-width="500px" persistent>
      <DiplomaEditor
        v-bind:editMode="diplomaDialog.editMode"
        v-bind:initialData="diplomaDialog.diploma"
        v-bind:saveLoading="diplomaDialog.saveLoading"
        v-bind:addMoreLoading="diplomaDialog.addMoreLoading"
        v-on:cancel="cancelDiploma"
        v-on:save="saveDiploma"
        v-on:addAnother="addAnother"
      />
    </v-dialog>

    <!-- Deactivate/archive confirmation -->
    <v-dialog
      v-model="deactivateDialog.show"
      max-width="350px"
      data-cy="diplomas-table-confirmation"
    >
      <v-card>
        <v-card-text>{{ t("diplomas.confirm-archive") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelDeactivate"
            color="secondary"
            variant="text"
            :disabled="deactivateDialog.loading"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deactivate(deactivateDialog.diploma)"
            color="primary"
            :disabled="deactivateDialog.loading"
            :loading="deactivateDialog.loading"
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
import { useRouter } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import { cloneDeep } from "lodash";
import DiplomaEditor from "./DiplomaEditor.vue";
import DiplomaAdminActions from "./DiplomaAdminActions.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const router = useRouter();

const diplomaDialog = ref({
  show: false,
  editMode: false,
  saveLoading: false,
  addMoreLoading: false,
  diploma: {} as Record<string, any>,
  courses: [] as any[]
});

const snackbar = ref({ show: false, text: "" });

const deactivateDialog = ref({
  show: false,
  diploma: {} as Record<string, any>,
  loading: false
});

const addMore = ref(false);
const tableLoaded = ref(false);
const diplomas = ref<any[]>([]);
const search = ref("");
const viewStatus = ref("active");

const headers = computed(() => [
  { title: t("diplomas.title"), value: "name", width: "40%" },
  { title: t("diplomas.description"), value: "description", width: "60%" },
  { title: t("actions.header"), sortable: false }
]);

const options = computed(() => [
  { title: t("actions.view-active"), value: "active" },
  { title: t("actions.view-archived"), value: "archived" },
  { title: t("actions.view-all"), value: "all" }
]);

const showDiplomas = computed(() => {
  switch (viewStatus.value) {
    case "active":
      return diplomas.value.filter(diploma => diploma.active);
    case "archived":
      return diplomas.value.filter(diploma => !diploma.active);
    case "all":
    default:
      return diplomas.value;
  }
});

function dispatchAction(actionName: string, diploma: any) {
  switch (actionName) {
    case "edit":
      editDiploma(diploma);
      break;
    case "deactivate":
      confirmDeactivate(diploma);
      break;
    case "activate":
      activate(diploma);
      break;
    default:
      break;
  }
}

function activateDiplomaDialog(diploma: Record<string, any> = {}, editMode = false) {
  diplomaDialog.value.editMode = editMode;
  diplomaDialog.value.diploma = diploma;
  diplomaDialog.value.show = true;
}

function editDiploma(diploma: any) {
  activateDiplomaDialog({ ...diploma }, true);
}

function newDiploma() {
  activateDiplomaDialog();
}

function confirmDeactivate(diploma: any) {
  deactivateDialog.value.show = true;
  deactivateDialog.value.diploma = diploma;
}

function cancelDeactivate() {
  deactivateDialog.value.show = false;
}

function deactivate(diploma: any) {
  deactivateDialog.value.loading = true;
  http
    .patch(`/api/v1/courses/diplomas/deactivate/${diploma.id}`)
    .then(resp => {
      let returnedDiploma = resp.data;
      const idx = diplomas.value.findIndex(d => d.id === returnedDiploma.id);
      diplomas.value[idx].active = false;
      showSnackbar(t("diplomas.archived"));
    })
    .catch(() => {
      showSnackbar(t("diplomas.update-failed"));
    })
    .finally(() => {
      deactivateDialog.value.loading = false;
      deactivateDialog.value.show = false;
    });
}

function activate(diploma: any) {
  http
    .patch(`/api/v1/courses/diplomas/activate/${diploma.id}`)
    .then(resp => {
      let returnedDiploma = resp.data;
      const idx = diplomas.value.findIndex(d => d.id === returnedDiploma.id);
      diplomas.value[idx].active = true;
      showSnackbar(t("diplomas.reactivated"));
    })
    .catch(() => {
      showSnackbar(t("diplomas.update-failed"));
    });
}

function clickThrough(diploma: any) {
  router.push({ name: "diploma-details", params: { diplomaId: diploma.id } });
}

function clearDiploma() {
  addMore.value = false;
  diplomaDialog.value.saveLoading = false;
  diplomaDialog.value.addMoreLoading = false;
  diplomaDialog.value.diploma = {};
}

function cancelDiploma() {
  addMore.value = false;
  diplomaDialog.value.show = false;
  diplomaDialog.value.saveLoading = false;
  diplomaDialog.value.addMoreLoading = false;
}

function addAnother(diploma: any) {
  addMore.value = true;
  diplomaDialog.value.addMoreLoading = true;
  saveDiploma(diploma);
}

function saveDiploma(diploma: any) {
  let diplomaClone = cloneDeep(diploma);
  const courses = diplomaClone.courseList || [];
  const courseIDList = courses.map((course: any) => course.id);
  delete diplomaClone.courseList;
  diplomaClone.courseList = courseIDList;

  if (diplomaDialog.value.editMode) {
    const diploma_id = diplomaClone.id;
    const idx = diplomas.value.findIndex(d => d.id === diplomaClone.id);
    delete diplomaClone.id;

    http
      .patch(`/api/v1/courses/diplomas/${diploma_id}`, diplomaClone)
      .then(resp => {
        console.log("UPDATED", resp);
        let updatedDiploma = resp.data;
        Object.assign(diplomas.value[idx], updatedDiploma);
        cancelDiploma();
        showSnackbar(t("diplomas.updated"));
      })
      .catch(err => {
        console.error("FAILURE", err.response);
        diplomaDialog.value.saveLoading = false;
        showSnackbar(t("diplomas.update-failed"));
      });
  } else {
    diplomaClone.active = true;
    http
      .post("/api/v1/courses/diplomas", diplomaClone)
      .then(resp => {
        console.log("ADDED", resp);
        let newDiploma = resp.data;
        diplomas.value.push(newDiploma);
        if (addMore.value) {
          clearDiploma();
        } else {
          cancelDiploma();
        }
        showSnackbar(t("diplomas.added"));
      })
      .catch(err => {
        console.error("FAILURE", err);
        diplomaDialog.value.saveLoading = false;
        diplomaDialog.value.addMoreLoading = false;
        showSnackbar(t("diplomas.add-failed"));
      });
  }
}

function showSnackbar(message: string) {
  snackbar.value.text = message;
  snackbar.value.show = true;
}

onMounted(() => {
  http.get("/api/v1/courses/diplomas").then(resp => {
    diplomas.value = resp.data;
    tableLoaded.value = true;
  });
});
</script>

<style scoped>
.hover-hand {
  cursor: pointer;
}
</style>
