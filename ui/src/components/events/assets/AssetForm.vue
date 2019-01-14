<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <!-- <v-text-field
          v-model="event.title"
          v-bind:label="$t('events.title')"
          name="title"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('title')"
          data-cy="title"
        ></v-text-field> -->
        <v-textarea
          rows="3"
          v-model="asset.description"
          v-bind:label="$t('events.assets.description')"
          name="description"
          v-bind:error-messages="errors.collect('description')"
          data-cy="description"
        ></v-textarea>

        <!-- <entity-search
        location
        searchEndpoint="http://localhost:3000/locations"
        v-on:setSelected="setLocation"/> -->
      </form>
    </v-card-text>
    <v-card-actions>
      <v-btn
        color="secondary"
        flat
        v-on:click="cancel"
        :disabled="formDisabled"
        data-cy="form-cancel"
        >{{ $t("actions.cancel") }}</v-btn
      >
      <v-spacer></v-spacer>
      <v-btn color="primary" flat v-on:click="clear" :disabled="formDisabled">{{
        $t("actions.clear")
      }}</v-btn>
      <v-btn
        color="primary"
        outline
        v-on:click="addAnother"
        v-if="editMode === false"
        :loading="addMoreLoading"
        :disabled="formDisabled"
        data-cy="form-addanother"
        >{{ $t("actions.add-another") }}</v-btn
      >
      <v-btn
        color="primary"
        raised
        v-on:click="save"
        :loading="saveLoading"
        :disabled="formDisabled"
        data-cy="form-save"
        >{{ $t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script>
import { isEmpty } from "lodash";
// import { mapGetters } from "vuex";
import EntitySearch from "../../EntitySearch";
export default {
  components: { "entity-search": EntitySearch },
  name: "AssetForm",
  watch: {
    // Make sure data stays in sync with any changes to `initialData` from parent.
    initialData(assetProp) {
      if (isEmpty(assetProp)) {
        this.clear();
      } else {
        this.asset = assetProp;
      }
    }
  },
  computed: {
    // List the keys in an Asset record.
    assetKeys() {
      return Object.keys(this.asset);
    },
    title() {
      return this.editMode
        ? this.$t("events.assets.edit-asset")
        : this.$t("events.assets.create-asset");
    },

    formDisabled() {
      return this.saveLoading || this.addMoreLoading;
    }

    // ...mapGetters(["currentLanguageCode"])
  },

  methods: {
    cancel() {
      this.clear();
      this.$emit("cancel");
    },

    // Clear the form and the validators.
    clear() {
      for (let key of this.assetKeys) {
        this.asset[key] = "";
      }

      this.$validator.reset();
    },

    save() {
      this.$validator.validateAll();
      if (!this.errors.any()) {
        // this.asset.active = true;
        this.$emit("save", this.asset);
      }
    },

    addAnother() {
      this.$validator.validateAll();
      if (!this.errors.any()) {
        this.$emit("add-another", this.asset);
      }
    }

    // setLocation(locationId) {
    //   console.log(locationId)
    // }
  },
  props: {
    editMode: {
      type: Boolean,
      required: true
    },
    initialData: {
      type: Object,
      required: true
    },
    saveLoading: {
      type: Boolean
    },
    addMoreLoading: {
      type: Boolean
    }
  },
  data: function() {
    return {
      asset: {},
      save_loading: false,
      add_more_loading: false
    };
  }
};
</script>
