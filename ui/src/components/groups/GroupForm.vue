<template>
  <!-- add a new group -->
  <v-card>
    <v-card-title>
      <span class="headline">{{ name }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-row column justify-center>
          <v-text-field
            v-model="group.name"
            v-bind:label="$t('groups.name')"
            name="title"
            v-validate="'required'"
            v-bind:error-messages="errors.first('title')"
            data-cy="title"
          />
          <v-textarea
            rows="3"
            v-model="group.description"
            v-bind:label="$t('groups.group-description')"
            name="description"
            v-validate="'required'"
            v-bind:error-messages="errors.collect('description')"
            data-cy="description"
          />
          <entity-type-form
            name="grouptype"
            entity-type-name="groupType"
            v-model="group.groupType"
            v-validate="'required'"
            v-bind:error-messages="errors.first('grouptype')"
          ></entity-type-form>
        </v-row>
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
        v-if="!editMode"
        :loading="addAnotherLoading"
        :disabled="formDisabled"
        data-cy="form-addanother"
        >{{ $t("actions.add-another") }}
      </v-btn>
      <v-btn
        color="primary"
        raised
        v-on:click="save"
        :loading="saveLoading"
        :disabled="formDisabled"
        data-cy="form-save"
        >{{ $t("actions.save") }}
        <!-- save botton - Add group -->
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { isEmpty } from "lodash";
import EntityTypeForm from "./EntityTypeForm";
export default {
  components: { EntityTypeForm },
  name: "GroupForm",
  watch: {
    initialData(groupProp) {
      if (isEmpty(groupProp)) {
        this.clear();
      } else {
        this.group = groupProp;
      }
    },
  },
  computed: {
    name() {
      return this.editMode
        ? this.$t("groups.edit-group")
        : this.$t("groups.create-group");
    },

    formDisabled() {
      return this.saveLoading || this.addAnotherLoading;
    },
  },

  methods: {
    validateGroup() {
      return this.$validator.validateAll();
    },

    cancel() {
      this.clear();
      this.$emit("cancel");
    },

    clear() {
      this.group = {};
      this.$validator.reset();
    },

    save() {
      //save add group
      this.validateGroup().then((valid) => {
        if (valid) {
          this.group.active = true;
          this.$emit("save", this.group); // send to parent component
        }
      });
    },

    addAnother() {
      this.validateGroup().then((valid) => {
        if (valid) {
          this.group.active = true;
          this.$emit("add-another", this.group);
          this.group = {};
          this.$validator.reset();
        }
      });
    },
  },
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
    addAnotherLoading: {
      type: Boolean,
    },
  },
  data: function () {
    return {
      group: {},
    };
  },
};
</script>
