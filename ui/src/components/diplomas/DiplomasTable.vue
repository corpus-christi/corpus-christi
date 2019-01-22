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


<!--
      <template slot="items" slot-scope="props">
        <tr @click="props.expanded = !props.expanded">
          <td>{{ props.item.name }}</td>
          <td>{{ props.item.description }}</td>
          <td>
            <DiplomaAdminActions
              v-bind:diploma="props.item"
              display-context="compact"
              v-on:action="dispatchAction($event, props.item)"
            />
          </td>
        </tr>
      </template>
      -->
      <!--
      <template slot="expand" slot-scope="props">
        <v-card flat>
          <v-card-text>
            <span class="font-weight-bold"
              >{{ $t("diplomas.courses-this-diploma") }}:</span
            >
            <ul>
              <li
                v-for="course in props.item.courseList"
                v-bind:key="course.id"
              >
                <span class="font-weight-bold">{{ course.name }}:</span>
                {{ course.description }}
              </li>
            </ul>
          </v-card-text>
        </v-card>
      </template>
      -->
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
        v-bind:diploma="diplomaDialog.diploma"
        v-bind:saving="diplomaDialog.saving"
        v-on:cancel="cancelDiploma"
        v-on:save="saveDiploma"
        v-on:clearForm="clearForm"
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
import { scrypt } from 'crypto';
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
        saving: false,
        diploma: {}
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
    clearForm() {
      this.diplomaDialog.diploma = {};
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
    cancelDiploma() {
      this.diplomaDialog.show = false;
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
          console.log("diploma deactivated", resp);
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
          console.log("diploma activated", resp);
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
      console.log(diploma);
      this.$router.push({ name: 'diploma-details', params: { diplomaId: diploma.id }})
    },

    saveDiploma(diploma) {
      console.log("diploma: ", diploma);
      this.diplomaDialog.saving = true;
      // just to be careful, make a clone of diploma, so not editing the object itself
      let diplomaClone = cloneDeep(diploma);
      // grab the courses
      const courses = diplomaClone.courseList || [];
      console.log("courses: ", courses);
      // create an array of course ids
      const courseIDList = courses.map(course => course.id);
      // Get rid of the courseList, which is an array of objects
      delete diplomaClone.courseList;
      // the api is expecting an array of course IDs, so add that property to diplomaClone
      diplomaClone.courseList = courseIDList;
      console.log("diplomaClone: ", diplomaClone);

      console.log("all diplomas: ", this.diplomas);

      if (this.diplomaDialog.editMode) {
        // Hang on to the ID of the diploma being updated.
        const diploma_id = diplomaClone.id;
        // Locate the diploma we're updating in the table.
        const idx = this.diplomas.findIndex(d => d.id === diplomaClone.id);
        // get rid of the id; not for consumption by the endpoint
        delete diplomaClone.id;
        console.log("diplomaClone: ", diplomaClone);

        this.$http
          .patch(`/api/v1/courses/diplomas/${diploma_id}`, diplomaClone)
          .then(resp => {
            console.log("UPDATED", resp);
            let updatedDiploma = resp.data;
            console.log(updatedDiploma);
            Object.assign(this.diplomas[idx], updatedDiploma);
            this.snackbar.text = this.$t("diplomas.updated");
            this.snackbar.show = true;
            console.log("diploma list: ", this.diplomas);
          })
          .catch(err => {
            console.error("FALURE", err.response);
            this.snackbar.text = this.$t("diplomas.update-failed");
            this.snackbar.show = true;
          })
          .finally(() => {
            this.diplomaDialog.show = false;
            this.diplomaDialog.saving = false;
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
            //console.log('new diploma list: ', this.diplomas);
          })
          .catch(err => {
            console.error("FAILURE", err);
            this.snackbar.text = this.$t("diplomas.add-failed");
            this.snackbar.show = true;
          })
          .finally(() => {
            this.diplomaDialog.show = false;
            this.diplomaDialog.saving = false;
          });
      }
    }
  },
  mounted: function() {
    this.$http.get("/api/v1/courses/diplomas").then(resp => {
      this.diplomas = resp.data;
      //console.log('diplomas received: ', this.diplomas);
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