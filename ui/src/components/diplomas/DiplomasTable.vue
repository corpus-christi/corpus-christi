<template>
    <div>
        <!-- Header -->
        <v-toolbar>
          <v-layout align-center justify-space-between fill-height>
            <v-flex md2>
              <v-toolbar-title>{{ $t("diplomas.diploma") }}</v-toolbar-title>
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
              <tr @click="props.expanded = !props.expanded">
                <td>{{ props.item.name }}</td>
                <td>{{ props.item.description }}</td>
                <td>
                <DiplomaAdminActions
                    v-bind:diploma="props.item"
                    display-context="compact"
                    v-on:action="dispatchAction($event, props.item)"/>
                </td>
              </tr>
            </template>
            <template slot="expand" slot-scope="props">
              <v-card flat>
                <v-card-text>
                  <span class="font-weight-bold">{{$t("diplomas.courses-this-diploma")}}:</span>
                  <ul>
                    <li 
                    v-for="course in props.item.courses"
                    v-bind:key="course.id"
                    >
                      <span class="font-weight-bold">{{ course.name }}:</span> {{course.description}}
                    </li>
                  </ul>
                </v-card-text>
              </v-card>
            </template>
        </v-data-table>
 
        <v-snackbar v-model="snackbar.show">
        {{ snackbar.text }}
            <v-btn flat @click="snackbar.show = false">
                {{ $t("actions.close") }}
            </v-btn>
        </v-snackbar>

        <!-- New/Edit dialog -->
        <v-dialog 
          v-model="diplomaDialog.show" 
          max-width="500px"
          persistent
        >
          <DiplomaEditor
              v-bind:editMode="diplomaDialog.editMode"
              v-bind:diploma="diplomaDialog.diploma"
              v-bind:saving="diplomaDialog.saving"
              v-on:cancel="cancelDiploma"
              v-on:save="saveDiploma"
              v-on:clearForm="clearForm"
          />
        </v-dialog>
    </div>
</template>

<script>
import DiplomaEditor from "./DiplomaEditor";
import DiplomaAdminActions from "./DiplomaAdminActions";
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
        { text: this.$t("diplomas.description"), value: "description", width: "60%" },
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
      switch(actionName) {
        case "edit":
          this.editDiploma(diploma);
          break;
        case "deactivate":
          // todo: deactivate diploma
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
    saveDiploma(diploma) {
      this.diplomaDialog.saving = true;

      // Hang onto the prereqs of the course
      const courses = diploma.courses || [];
      // Get rid of the prereqs; not for consumption by the endpoint
      delete diploma.prerequisites;

      if (this.diplomaDialog.editMode) {
        // Hang on to the ID of the diploma being updated.
        const diploma_id = diploma.id;
        // Locate the diploma we're updating in the table.
        const idx = this.diplomas.findIndex(d => d.id === diploma.id);
        // Get rid of the ID; not for consumption by endpoint.
        delete diploma.id;

        let promises = [];
        promises.push(
          this.$http
            //.patch(`/api/v1/courses/diplomas/${diploma_id}`, course)
            // FIX!!!
            .patch(`http://localhost:3000/diplomas/${diploma_id}`, diploma)
            .then(resp => {
              console.log("EDITED", resp);
              Object.assign(this.diplomas[idx], diploma);
            })
        );
        promises.push(
          this.$http.patch(
            `/api/v1/courses/diplomas/courses/${diploma_id}`,
            { courses: courses.map(course => course.id) }
          ) // API expects array of IDs
        );

        Promise.all(promises)
          .then(() => {
            this.diplomas[idx].courses = courses;
            this.snackbar.text = this.$t("diplomas.updated");
            this.snackbar.show = true;
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
        diploma.active = true;
        this.$http
          .post("/api/v1/courses/diplomas", diploma)
          .then(resp => {
            console.log("ADDED", resp);
            let newDiploma = resp.data;
            newDiploma.courses = courses; // Re-attach courses so they show up in UI
            this.diplomas.push(newDiploma);

            // Now that diploma is created, add courses to it
            return this.$http.patch(
              `/api/v1/courses/diplomas/courses/${newDiploma.id}`,
              { courses: courses.map(course => course.id) }
            ); // API expects array of IDs
          })
          .then(resp => {
            console.log("COURSES", resp);
            this.snackbar.text = this.$t("diplomas.added");
            this.snackbar.show = true;
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
    this.$http
      .get("/api/v1/courses/diplomas")
      .then(resp => {
        this.diplomas = resp.data;
        this.tableLoaded = true;
      });
  }
};

</script>

<style>

</style>
