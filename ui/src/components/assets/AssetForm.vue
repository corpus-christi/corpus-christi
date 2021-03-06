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

        <v-btn
          small
          color="primary"
          text
          :disabled="addressWasSaved"
          @click="changeAddressView(true)"
        >
          {{ $t("actions.add-address") }}
        </v-btn>

        <address-form
          v-if="showAddressForm"
          @cancel="changeAddressView"
          @saved="saveAddress"
        >
        </address-form>

        <entity-search
          location
          name="location"
          v-model="asset.location"
          v-validate="checkLocation"
          v-bind:error-messages="errors.first('location')"
        />
      </form>
    </v-card-text>
    <v-card-actions>
      <v-btn
        color="secondary"
        text
        v-on:click="cancel"
        :disabled="formDisabled"
        data-cy="form-cancel"
        >{{ $t("actions.cancel") }}</v-btn
      >
      <v-spacer />
      <v-btn
        color="primary"
        outlined
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
import AddressForm from "../AddressForm.vue";

export default {
  components: { "entity-search": EntitySearch, "address-form": AddressForm },
  name: "AssetForm",
  props: {
    editMode: {
      type: Boolean,
      required: true,
    },
    initialData: {
      type: Object,
      required: true,
    },
    saveLoading: {
      type: Boolean,
    },
    addMoreLoading: {
      type: Boolean,
    },
  },
  data: function () {
    return {
      showAddressForm: false,
      addressWasSaved: false,
      asset: {},
      save_loading: false,
      add_more_loading: false,
      addMore: false,
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
    },
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
    },

    addressSaved() {
      return this.addressWasSaved;
    },
  },

  methods: {
    checkLocation() {
      return this.asset.location;
    },

    cancel() {
      this.$emit("cancel");
    },

    // Clear the form and the validators.
    clear() {
      this.addressWasSaved = false;
      delete this.asset.location;
      for (let key of this.assetKeys) {
        this.asset[key] = "";
      }

      this.$validator.reset();
    },

    save() {
      this.$validator.validateAll().then(() => {
        console.log("validating", this.asset);
        if (!this.errors.any()) {
          this.asset.active = true;
          if (this.addMore) this.$emit("addAnother", this.asset);
          else this.$emit("save", this.asset);
          this.addressWasSaved = false;
        }
        this.addMore = false;
      });
    },

    saveAddress(resp) {
      console.log("saving", this.asset);
      this.asset.location = resp;
      this.addressWasSaved = true;
      this.showAddressForm = false;
      this.save();
    },

    changeAddressView(show) {
      this.showAddressForm = show;
    },

    addAnother() {
      this.addMore = true;
      this.save();
    },
  },
};
</script>
