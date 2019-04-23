<template>
  <div>
    <!-- Header -->
    <v-toolbar>
      <v-layout align-center justify-space-between fill-height>
        <v-flex md2>
          <v-toolbar-title>{{ $t("diplomas.diplomas") }}</v-toolbar-title>
        </v-flex>
        <v-spacer></v-spacer>
        <v-flex md3>
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="$t('actions.search')"
            single-line
            hide-details
            data-cy="diplomas-table-search"
          ></v-text-field>
        </v-flex>
        <v-spacer></v-spacer>
        <v-flex md3>
          <v-select
            v-model="viewStatus"
            :items="options"
            solo
            hide-details
            data-cy="diplomas-table-viewstatus"
          ></v-select>
        </v-flex>

        <v-flex shrink justify-self-end>
          <v-btn
            color="primary"
            raised
            v-on:click.stop="newDiploma"
            data-cy="diplomas-table-new"
          >
            <v-icon left>library_add</v-icon>
            {{ $t("diplomas.new") }}
          </v-btn>
        </v-flex>
      </v-layout>
    </v-toolbar>

    <!-- Table of existing people -->
    <v-data-table
      :headers="headers"
      :items="showDiplomas"
      :loading="!tableLoaded"
      :search="search"
      class="elevation-1"
      data-cy="diplomas-table"
    >
      <template slot="items" slot-scope="props">
        <tr>
          <td class="hover-hand" @click="clickThrough(props.item)">
            {{ props.item.name }}
          </td>
          <td class="hover-hand" @click="clickThrough(props.item)">
            {{ props.item.description }}
          </td>
          <td class="hover-hand" @click="clickThrough(props.item)">
            <DiplomaAdminActions
              v-bind:diploma="props.item"
              display-context="compact"
              v-on:action="dispatchAction($event, props.item)"
            />
          </td>
        </tr>
      </template>
    </v-data-table>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false">{{
        $t("actions.close")
      }}</v-btn>
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
        v-on:clearForm="clearDiploma"
      />
    </v-dialog>

    <!-- Deactivate/archive confirmation -->
    <v-dialog
      v-model="deactivateDialog.show"
      max-width="350px"
      data-cy="diplomas-table-confirmation"
    >
      <v-card>
        <v-card-text>{{ $t("diplomas.confirm-archive") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelDeactivate"
            color="secondary"
            flat
            :disabled="deactivateDialog.loading"
            >{{ $t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deactivate(deactivateDialog.diploma)"
            color="primary"
            raised
            :disabled="deactivateDialog.loading"
            :loading="deactivateDialog.loading"
            >{{ $t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import DiplomaEditor from "./DiplomaEditor";
import DiplomaAdminActions from "./DiplomaAdminActions";
import { cloneDeep } from "lodash";
export default {
  name: "DiplomasTable",
  components: {
    DiplomaEditor,
    DiplomaAdminActions
  },
  data() {
    return {
      diplomaDialog: {
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        diploma: {},
        courses: []
      },
      snackbar: {
        show: false,
        text: ""
      },
      deactivateDialog: {
        show: false,
        course: {},
        loading: false
      },
      addMore: false,
      tableLoaded: false,
      selected: [],
      diplomas: [],
      search: "",
      viewStatus: "active"
    };
  },
  computed: {
    // Put here so that the headers are reactive.
    headers() {
      return [
        { text: this.$t("diplomas.title"), value: "name", width: "40%" },
        {
          text: this.$t("diplomas.description"),
          value: "description",
          width: "60%"
        },
        { text: this.$t("actions.header"), sortable: false }
      ];
    },
    options() {
      return [
        { text: this.$t("actions.view-active"), value: "active" },
        { text: this.$t("actions.view-archived"), value: "archived" },
        { text: this.$t("actions.view-all"), value: "all" }
      ];
    },
    showDiplomas() {
      switch (this.viewStatus) {
        case "active":
          return this.diplomas.filter(diploma => diploma.active);
        case "archived":
          return this.diplomas.filter(diploma => !diploma.active);
        case "all":
        default:
          return this.diplomas;
      }
    }
  },

  methods: {
    dispatchAction(actionName, diploma) {
      switch (actionName) {
        case "edit":
          this.editDiploma(diploma);
          break;
        case "deactivate":
          this.confirmDeactivate(diploma);
          break;
        case "activate":
          this.activate(diploma);
          break;
        default:
          break;
      }
    },

    activateDiplomaDialog(diploma = {}, editMode = false) {
      this.diplomaDialog.editMode = editMode;
      this.diplomaDialog.diploma = diploma;
      this.diplomaDialog.show = true;
    },
    editDiploma(diploma) {
      this.activateDiplomaDialog({ ...diploma }, true);
    },
    newDiploma() {
      this.activateDiplomaDialog();
    },
    confirmDeactivate(diploma) {
      this.deactivateDialog.show = true;
      this.deactivateDialog.diploma = diploma;
    },
    cancelDeactivate() {
      this.deactivateDialog.show = false;
    },
    deactivate(diploma) {
      this.deactivateDialog.loading = true;
      this.$http
        .patch(`/api/v1/courses/diplomas/deactivate/${diploma.id}`)
        .then(resp => {
          let returnedDiploma = resp.data;
          const idx = this.diplomas.findIndex(d => d.id === returnedDiploma.id);
          this.diplomas[idx].active = false;
          this.snackbar.text = this.$t("diplomas.archived");
          this.snackbar.show = true;
        })
        .catch(() => {
          this.snackbar.text = this.$t("diplomas.update-failed");
          this.snackbar.show = true;
        })
        .finally(() => {
          this.deactivateDialog.loading = false;
          this.deactivateDialog.show = false;
        });
    },

    activate(diploma) {
      this.$http
        .patch(`/api/v1/courses/diplomas/activate/${diploma.id}`)
        .then(resp => {
          let returnedDiploma = resp.data;
          const idx = this.diplomas.findIndex(d => d.id === returnedDiploma.id);
          this.diplomas[idx].active = true;
          this.snackbar.text = this.$t("diplomas.reactivated");
          this.snackbar.show = true;
        })
        .catch(() => {
          this.snackbar.text = this.$t("diplomas.update-failed");
          this.snackbar.show = true;
        });
    },

    clickThrough(diploma) {
      this.$router.push({
        name: "diploma-details",
        params: { diplomaId: diploma.id }
      });
    },

    clearDiploma() {
      this.addMore = false;
      this.diplomaDialog.saveLoading = false;
      this.diplomaDialog.addMoreLoading = false;
      this.diplomaDialog.diploma = {};
    },

    cancelDiploma() {
      this.addMore = false;
      this.diplomaDialog.show = false;
      this.diplomaDialog.saveLoading = false;
      this.diplomaDialog.addMoreLoading = false;
    },

    addAnother(diploma) {
      this.addMore = true;
      this.diplomaDialog.addMoreLoading = true;
      this.saveDiploma(diploma);
    },

    save(diploma) {
      this.diplomaDialog.saveLoading = true;
      this.saveDiploma(diploma);
    },

    saveDiploma(diploma) {
      // just to be careful, make a clone of diploma, so not editing the object itself
      let diplomaClone = cloneDeep(diploma);
      // grab the courses
      const courses = diplomaClone.courseList || [];
      // create an array of course ids
      const courseIDList = courses.map(course => course.id);
      // Get rid of the courseList, which is an array of objects
      delete diplomaClone.courseList;
      // the api is expecting an array of course IDs, so add that property to diplomaClone
      diplomaClone.courseList = courseIDList;
      if (this.diplomaDialog.editMode) {
        // Hang on to the ID of the diploma being updated.
        const diploma_id = diplomaClone.id;
        // Locate the diploma we're updating in the table.
        const idx = this.diplomas.findIndex(d => d.id === diplomaClone.id);
        // get rid of the id; not for consumption by the endpoint
        delete diplomaClone.id;

        this.$http
          .patch(`/api/v1/courses/diplomas/${diploma_id}`, diplomaClone)
          .then(resp => {
            console.log("UPDATED", resp);
            let updatedDiploma = resp.data;
            Object.assign(this.diplomas[idx], updatedDiploma);
            this.cancelDiploma();
            this.showSnackbar(this.$t("diplomas.updated"));
          })
          .catch(err => {
            console.error("FALURE", err.response);
            this.diplomaDialog.saveLoading = false;
            this.showSnackbar(this.$t("diplomas.update-failed"));
          });
      } else {
        // All new diplomas are active
        diplomaClone.active = true;
        this.$http
          .post("/api/v1/courses/diplomas", diplomaClone)
          .then(resp => {
            console.log("ADDED", resp);
            let newDiploma = resp.data;
            this.diplomas.push(newDiploma);
            if (this.addMore) {
              this.clearDiploma();
            } else {
              this.cancelDiploma();
            }
            this.showSnackbar(this.$t("diplomas.added"));
          })
          .catch(err => {
            console.error("FAILURE", err);
            this.diplomaDialog.saveLoading = false;
            this.diplomaDialog.addMoreLoading = false;
            this.showSnackbar(this.$t("diplomas.add-failed"));
          });
      }
    },
    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    }
  },
  mounted: function() {
    this.$http.get("/api/v1/courses/diplomas").then(resp => {
      this.diplomas = resp.data;
      this.tableLoaded = true;
    });
  }
};
</script>

<style scoped>
.hover-hand {
  cursor: pointer;
}
</style>
