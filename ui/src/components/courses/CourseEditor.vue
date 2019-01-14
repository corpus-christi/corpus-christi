<template>
  <v-card>
    <v-card-title data-cy="course-editor-title">
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <CourseForm ref="form" v-bind:course="course" />
    </v-card-text>
    <v-card-actions data-cy="course-editor-actions">
      <v-btn color="secondary" flat :disabled="saving" v-on:click="cancel">
        {{ $t("actions.cancel") }}
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn color="primary" flat :disabled="saving" v-on:click="clear">
        {{ $t("actions.clear") }}
      </v-btn>
      <v-btn
        color="primary"
        raised
        :disabled="saving"
        :loading="saving"
        v-on:click="save"
      >
        {{ $t("actions.save") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { isEmpty } from "lodash";
import CourseForm from "./CourseForm";

export default {
  name: "CourseEditor",
  components: {
    CourseForm
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
    saving: {
      type: Boolean,
      default: false
    }
  },
  data: function() {
    return {
      course: {}
    };
  },
  computed: {
    title() {
      return this.editMode ? this.$t("actions.edit") : this.$t("courses.new");
    }
  },

  watch: {
    // Make sure data stays in sync with any changes to `initialData` from parent.
    initialData(courseProp) {
      if (isEmpty(courseProp)) {
        this.clear();
      } else {
        this.course = courseProp;
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
      this.course = {};
      this.$refs.form.$validator.reset();
    },

    // Trigger a save event, returning the updated `Course`.
    save() {
      this.$refs.form.$validator.validateAll();
      if (!this.$refs.form.errors.any()) {
        this.$emit("save", this.course);
      }
    }
  }
};
</script>