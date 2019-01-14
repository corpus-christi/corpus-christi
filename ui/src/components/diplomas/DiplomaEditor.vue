<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ name }}</span>
    </v-card-title>
    <v-card-text>
      <DiplomaForm ref="form" v-bind:diploma="diploma"/>
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
      diploma: {}
    };
  },
  computed: {
    name() {
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
        this.diploma = diplomaProp;
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
      this.diploma = {};
      this.$refs.form.$validator.reset();
    },
    // Trigger a save event, returning the updated `Diploma`.
    save() {
      this.$refs.form.$validator.validateAll();
      console.log('diploma in editor: ', this.diploma);
      console.log('form errors: ', this.$refs.form.$validator);

      if (!this.$refs.form.errors.any()) {
        console.log('form has no errors');
        this.$emit("save", this.diploma);
      } else {
        console.log('the form contains errors!', this.$refs.form.errors);
      }
 
    }
    /*,
    remove(item) {
      this.prereqs.splice(this.prereqs.indexOf(item), 1);
      this.prereqs = [...this.prereqs];
    }
    */
  }
};
</script>