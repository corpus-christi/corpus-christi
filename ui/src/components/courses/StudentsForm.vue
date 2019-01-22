<template>
  <v-card>
    <v-card-title primary-title>
      <div>
        <h3 class="headline mb-0">
          {{ $t("person.actions.add-participant") }}
        </h3>
      </div>
    </v-card-title>
    <v-card-text>
      <form><entity-search person v-model="newStudent" /></form>
    </v-card-text>

    <v-card-actions>
      <v-btn
        color="secondary"
        flat
        :disabled="saving"
        v-on:click="cancel"
        data-cy="studentform-cancel"
        >{{ $t("actions.cancel") }}
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        raised
        :disabled="Object.keys(newStudent).length == 0"
        :loading="saving"
        v-on:click="save"
        data-cy="studentform-save"
        >{{ $t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script>
import EntitySearch from "../EntitySearch";
import { mapGetters } from "vuex";
import { isEmpty } from "lodash";

export default {
  name: "StudentsForm",
  components: {
    EntitySearch
  },
  data: function() {
    return {
      newStudent: {}
    };
  },

  computed: {
    title() {
      return this.$t("courses.new-offering");
    },

    ...mapGetters(["currentLanguageCode"])
  },

  watch: {
    // Make sure data stays in sync with any changes to `initialData` from parent.
    initialData(studentProp) {
      if (isEmpty(studentProp)) {
        this.clear();
      } else {
        this.newStudent = studentProp;
      }
    }
  },

  props: {
    initialData: {
      type: Object,
      required: true
    },
    saving: {
      type: Boolean,
      default: false
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
      this.newStudent = {};
      this.$validator.reset();
    },

    // Trigger a save event, returning the updated `Course Offering`.
    save() {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          this.$emit("save", this.newStudent);
        }
      });
    }
  }
};
</script>
