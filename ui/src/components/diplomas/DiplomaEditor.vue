<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <DiplomaForm ref="form" v-for="diploma in diplomas" :key="diploma.id" v-bind:diploma="diploma"/>
    </v-card-text>
    <v-card-actions>
      <v-btn color="secondary" flat v-on:click="cancel">
        {{ $t("actions.cancel") }}
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn color="primary" flat v-on:click="clear">
        {{ $t("actions.clear") }}
      </v-btn>
      <v-btn color="primary" raised v-on:click="save">
        {{ $t("actions.save") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { isEmpty } from "lodash";
import DiplomaForm from "./DiplomaForm";
export default {
  name: "DiplomaEditor",
  components: {
    DiplomaForm
  },
  props: {
    editMode: {
      type: Boolean,
      required: true
    },
    initialData: {
      type: Object,
      required: true
    }
  },
  data: function() {
    return {
      diplomas: [{}]
    };
  },
  computed: {
    title() {
      return this.editMode
        ? this.$t("actions.edit")
        : this.$t("diplomas.new");
    },
  },
  watch: {
    // Make sure data stays in sync with any changes to `initialData` from parent.
    initialData(diplomaProp) {
      if (isEmpty(diplomaProp)) {
        this.clear();
      } else {
        this.diplomas = [diplomaProp];
      }
    }
  },
  methods: {
    // Abandon ship.
    cancel() {
      this.clear();
      this.$emit("cancel");
    },
    // Clear the forms.
    clear() {
      this.diplomas = [{}];
    },
    // Trigger a save event, returning the updated `Diploma`.
    save() {
      this.$refs.form[0].$validator.validateAll();
      if (!this.errors.any()) {
        this.$emit("save", this.diplomas);
      }
    },
    remove(item) {
      this.prereqs.splice(this.prereqs.indexOf(item), 1);
      this.prereqs = [...this.prereqs];
    }
  }
};
</script>