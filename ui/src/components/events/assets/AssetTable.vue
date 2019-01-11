<template>
  <div>
    <v-toolbar>
      <v-toolbar-title>{{ $t("events.assets.title") }}</v-toolbar-title>
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
        v-on:click.stop="newAsset"
        data-cy="add-event"
      >
        <v-icon dark left>add</v-icon>
        {{ $t("events.assets.new") }}
      </v-btn>
    </v-toolbar>

    <v-data-table :headers="headers" :items="assets" :search="search" class="elevation-1">
      <template slot="items" slot-scope="props">
        <td class="hover-hand" v-on:click="$router.push({path: '/events/' + props.item.id})">{{ props.item.description }}</td>
        <td class="hover-hand" v-on:click="$router.push({path: '/events/' + props.item.id})">{{ props.item.location_name }}</td>
        <td>
          <v-tooltip bottom v-if="props.item.active">
            <v-btn
              icon
              outline
              small
              color="primary"
              slot="activator"
              v-on:click="editAsset(props.item)"
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
            >
              <v-icon small>filter_none</v-icon>
            </v-btn>
            <span>{{ $t("actions.duplicate") }}</span>
          </v-tooltip>
          <v-tooltip bottom  v-if="props.item.active">
            <v-btn
              icon
              outline
              small
              color="primary"
              slot="activator"
              v-on:click="confirmArchive(props.item)"
            >
              <v-icon small>archive</v-icon>
            </v-btn>
            <span>{{ $t("actions.tooltips.archive") }}</span>
          </v-tooltip>
          <v-tooltip bottom  v-if="!props.item.active">
            <v-btn
              icon
              outline
              small
              color="primary"
              slot="activator"
              v-on:click="unarchive(props.item)"
              :loading="props.item.unarchiving"
            >
              <v-icon small>unarchive</v-icon>
            </v-btn>
            <span>{{ $t("actions.tooltips.unarchive") }}</span>
          </v-tooltip>
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
    <v-dialog v-model="assetDialog.show" max-width="500px">
      <asset-form
        v-bind:editMode="assetDialog.editMode"
        v-bind:initialData="assetDialog.asset"
        v-on:cancel="cancelAsset"
      />
    </v-dialog>

    <!-- v-bind:saveLoading="assetDialog.saveLoading"
    v-bind:addMoreLoading="assetDialog.addMoreLoading"
    v-on:add-another="addAnotherAsset"
    v-on:save="saveAsset" -->


  </div>
</template>

<script>
import AssetForm from "./AssetForm";

export default {
  name: "AssetTable",
  components: { "asset-form": AssetForm },
  // mounted() {
  //   this.$http.get("http://localhost:3000/events").then(resp => {
  //     this.events = resp.data;
  //   });
  // },

  data() {
    return {
      assets: [],
      assetDialog: {
        show: false,
        editMode: false,
        // saveLoading: false,
        // addMoreLoading: false,
        asset: {}
      },
      search: "",

      snackbar: {
        show: false,
        text: ""
      }
    };
  },
  computed: {
    headers() {
      return [
        { text: this.$t("events.assets.description"), value: "description" },
        { text: this.$t("events.assets.location"), value: "location_name" },
        { text: this.$t("events.actions"), sortable: false }
      ];
    },
    // ...mapGetters(["currentLanguageCode"])
  },
  methods: {
    activateAssetDialog(asset = {}, editMode = false) {
      this.assetDialog.editMode = editMode;
      this.assetDialog.asset = asset;
      this.assetDialog.show = true;
    },

    editAsset(asset) {
      this.activateAssetDialog({ ...asset }, true);
    },

    // activateArchiveDialog(assetId) {
    //   this.archiveDialog.show = true;
    //   this.archiveDialog.assetId = assetId;
    // },

    // confirmArchive(asset) {
    //   this.activateArchiveDialog(asset.id);
    // },

    duplicate(asset) {
      const copyAsset = JSON.parse(JSON.stringify(event));
      delete copyAsset.id;
      this.activateAssetDialog(copyAsset);
    },
    
    // archiveAsset() {
    //   console.log("Archived asset")
    //   this.archiveDialog.loading = true;
    //   const assetId = this.archiveDialog.assetId
    //   const idx = this.assets.findIndex(ev => ev.id === assetId);
    //   this.$http
    //     .delete(`http://localhost:3000/events/${eventId}`)
    //     .then(resp => {
    //       console.log("ARCHIVE", resp);
    //       this.assets[idx].active = false;
    //       this.archiveDialog.loading = false;
    //       this.archiveDialog.show = false;
    //       this.showSnackbar(this.$t("events.assets.asset-archived"));
    //     })
    //     .catch(err => {
    //       console.error("ARCHIVE FALURE", err.response);
    //       this.archiveDialog.loading = false;
    //       this.archiveDialog.show = false;
    //       this.showSnackbar(this.$t("events.assets.error-archiving-asset"));
    //     });

    //   // this.archiveDialog.show = false;
    // },

    // unarchive(event) {
    //   const idx = this.events.findIndex(ev => ev.id === event.id);
    //   const copyEvent = JSON.parse(JSON.stringify(event));
    //   event.unarchiving = true;
    //   copyEvent.active = true;
    //   this.$http
    //     .put(`http://localhost:3000/events/${copyEvent.id}`, copyEvent)
    //     .then(resp => {
    //       console.log("UNARCHIVED", resp);
    //       Object.assign(this.events[idx], resp.data);
    //       this.showSnackbar(this.$t("events.event-unarchived"));
    //     })
    //     .catch(err => {
    //       delete event.unarchiving;
    //       console.error("UNARCHIVE FALURE", err.response);
    //       this.showSnackbar(this.$t("events.error-unarchiving-event"));
    //     });
    // },

    cancelArchive() {
      this.archiveDialog.show = false;
    },

    newAsset() {
      this.activateAssetDialog();
    },

    cancelAsset() {
      this.assetDialog.show = false;
    },

    // saveEvent(event) {
    //   this.eventDialog.saveLoading = true;
    //   if (this.eventDialog.editMode) {
    //     const eventId = event.id;
    //     const idx = this.events.findIndex(ev => ev.id === event.id);
    //     delete event.id;
    //     this.$http
    //       .put(`http://localhost:3000/events/${eventId}`, event)
    //       .then(resp => {
    //         console.log("EDITED", resp);
    //         Object.assign(this.events[idx], event);
    //         this.eventDialog.show = false;
    //         this.eventDialog.saveLoading = false;
    //         this.showSnackbar(this.$t("events.assets.asset-edited"));
    //       })
    //       .catch(err => {
    //         console.error("PUT FALURE", err.response);
    //         this.eventDialog.saveLoading = false;
    //         this.showSnackbar(this.$t("events.assets.error-editing-asset"));
    //       });
    //   } else {
    //     this.$http
    //       .post("http://localhost:3000/events/", event)
    //       .then(resp => {
    //         console.log("ADDED", resp);
    //         this.events.push(resp.data);
    //         this.eventDialog.show = false;
    //         this.eventDialog.saveLoading = false;
    //         this.showSnackbar(this.$t("events.assets.asset-added"));
    //       })
    //       .catch(err => {
    //         console.error("POST FAILURE", err.response);
    //         this.eventDialog.saveLoading = false;
    //         this.showSnackbar(this.$t("events.assets.error-adding-asset"));
    //       });
    //   }
    // },

    // addAnotherAsset(asset) {
    //   this.assetDialog.addMoreLoading = true;
    //   this.$http
    //       .post("http://localhost:3000/events/", event)
    //       .then(resp => {
    //         console.log("ADDED", resp);
    //         this.events.push(resp.data);
    //         this.eventDialog.show = false;
    //         this.eventDialog.saveLoading = false;
    //         this.showSnackbar(this.$t("events.assets.asset-added"));
    //       })
    //       .catch(err => {
    //         console.error("FAILURE", err.response);
    //         this.eventDialog.saveLoading = false;
    //         this.showSnackbar(this.$t("events.assets.error-adding-asset"));
    //       });
    // },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },
  }
};
</script>