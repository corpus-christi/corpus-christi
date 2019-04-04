<template>
  <v-card>
    <v-card-title data-cy="course-editor-title">
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text> <CourseForm ref="form" :course="course" /> </v-card-text>
    <v-card-actions data-cy="course-editor-actions">
      <v-btn
        color="secondary"
        flat
        :disabled="formDisabled"
        v-on:click="cancel"
      >
        {{ $t("actions.cancel") }}
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        outline
        v-on:click="addAnother"
        v-if="!editMode"
        :loading="addMoreLoading"
        :disabled="formDisabled"
        data-cy="add-another"
        >{{ $t("actions.add-another") }}</v-btn
      >
      <v-btn
        color="primary"
        raised
        :loading="saveLoading"
        :disabled="formDisabled"
        v-on:click="save"
      >
        {{ $t("actions.save") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { isEmpty, cloneDeep } from "lodash";
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
    saveLoading: {
      type: Boolean
    },
    addMoreLoading: {
      type: Boolean
    }
  },
  data: function() {
    return {
      course: {},
      addMore: false
    };
  },
  computed: {
    title() {
      return this.editMode ? this.$t("actions.edit") : this.$t("courses.new");
    },
    formDisabled() {
      return this.saveLoading || this.addMoreLoading;
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

    addAnother() {
      this.addMore = true;
      this.save();
    },

    save() {
      this.$refs.form.$validator.validateAll().then(() => {
        if (!this.$refs.form.errors.any()) {
          let course = cloneDeep(this.course);
          if (this.addMore) this.$emit("addAnother", course);
          else this.$emit("save", course);
        }
        this.addMore = false;
      });
    }
  }
};
</script>
