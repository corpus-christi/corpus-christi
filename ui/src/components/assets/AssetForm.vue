<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-textarea
          rows="3"
          v-model="asset.description"
          v-bind:label="$t('assets.description')"
          name="description"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('description')"
          data-cy="description"
        ></v-textarea>

        <entity-search
          location
          name="location"
          v-model="asset.location"
          v-validate="'required'"
          v-bind:error-messages="errors.first('location')"
        />
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
import EntitySearch from "../EntitySearch";
export default {
  components: { "entity-search": EntitySearch },
  name: "AssetForm",
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
      add_more_loading: false,
      addMore: false
    };
  },

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
        ? this.$t("assets.edit-asset")
        : this.$t("assets.create-asset");
    },

    formDisabled() {
      return this.saveLoading || this.addMoreLoading;
    }
  },

  methods: {
    cancel() {
      this.$emit("cancel");
    },

    // Clear the form and the validators.
    clear() {
      delete this.asset.location;
      for (let key of this.assetKeys) {
        this.asset[key] = "";
      }

      this.$validator.reset();
    },

    save() {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          this.asset.active = true;
          if (this.addMore) this.$emit("addAnother", this.asset);
          else this.$emit("save", this.asset);
        }
        this.addMore = false;
      });
    },

    addAnother() {
      this.addMore = true;
      this.save();
    }
  }
};
</script>
