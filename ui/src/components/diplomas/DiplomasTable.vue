<template>
    <div>
        <!-- Header -->
        <v-toolbar>
            <v-toolbar-title> {{ $t("diplomas.diploma") }}</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-text-field
                v-model="search"
                append-icon="search"
                v-bind:label="$t('actions.search')"
                single-line
                hide-details
            ></v-text-field>
            <v-spacer></v-spacer>

            <v-btn
                color="primary"
                raised
                v-on:click.stop="newDiploma"
            >
                <v-icon left>library_add</v-icon>
                {{$t('diplomas.new')}}
            </v-btn>
        </v-toolbar>

        <!-- Table of existing people -->
        <v-data-table
        :headers="headers"
        :items="diplomas"
        :search="search"
        class="elevation-1"
        >
            <template slot="items" slot-scope="props">
                <td>{{ props.item.title }}</td>
                <td>{{ props.item.description }}</td>
                <td>
                <DiplomaAdminActions
                    v-bind:diploma="props.item"
                    display-context="compact"
                    v-on:action="dispatchAction($event, props.item)"/>
                </td>
            </template>
        </v-data-table>
 
        <v-snackbar v-model="snackbar.show">
        {{ snackbar.text }}
            <v-btn flat @click="snackbar.show = false">
                {{ $t("actions.close") }}
            </v-btn>
        </v-snackbar>

        <!-- New/Edit dialog -->
        <v-dialog v-model="diplomaDialog.show" max-width="500px">
        <DiplomaEditor
            v-bind:editMode="diplomaDialog.editMode"
            v-bind:initialData="diplomaDialog.diploma"
            v-on:cancel="cancelDiploma"
            v-on:save="saveDiploma"
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
        diploma: {}
      },
      snackbar: {
        show: false,
        text: ""
      },
      selected: [],
      diplomas: [],
      search: "",
    };
  },
  computed: {
    // Put here so that the headers are reactive.
    headers() {
      return [
        { text: this.$t("diplomas.title"), value: "title", width: "40%" },
        { text: this.$t("diplomas.description"), value: "description", width: "60%" },
        { text: this.$t("actions.header"), sortable: false }
      ];
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
      if (this.diplomaDialog.editMode) {
        // Hang on to the ID of the person being updated.
        const diploma_id = diploma.id;
        // Locate the person we're updating in the table.
        const idx = this.diplomas.findIndex(c => c.id === diploma.id);
        // Get rid of the ID; not for consumption by endpoint.
        delete diploma.id;
        this.$http
          .put(`/api/v1/courses/diplomas/${diploma_id}`, diploma)
          .then(resp => {
            console.log("EDITED", resp);
            Object.assign(this.diplomas[idx], diploma);
          })
          .catch(err => console.error("FALURE", err.response));
      } else {
        this.$http
          .post("/api/v1/courses/diplomas", diploma)
          .then(resp => {
            console.log("ADDED", resp);
            this.diplomas.push(resp.data);
          })
          .catch(err => console.error("FAILURE", err.response));
      }
      this.diplomaDialog.show = false;
    }
  },
  mounted: function() {
    this.$http
      .get("/api/v1/courses/diplomas")
      .then(resp => (this.diplomas = resp.data));
  }
};

</script>

<style>

</style>
