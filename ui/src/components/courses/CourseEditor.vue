<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <CourseForm ref="form" v-bind:course="course"/>
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
    }
  },
  data: function() {
    return {
      course: {
        title: "",
        description: ""
      }
    };
  },
  computed: {
    title() {
      return this.editMode
        ? this.$t("actions.edit")
        : this.$t("courses.new");
    },
    // List the keys in a course record.
    courseKeys() {
      return Object.keys(this.course);
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

    // Clear the form and the validators.
    clear() {
      for (let key of this.courseKeys) {
        this.course[key] = "";
      }
      this.$refs.form.$validator.reset();
    },

    // Trigger a save event, returning the update `Person`.
    save() {
      this.$validator.validateAll();
      if (!this.errors.any()) {
        this.$emit("save", this.course);
      }
    },

    remove(item) {
      this.prereqs.splice(this.prereqs.indexOf(item), 1);
      this.prereqs = [...this.prereqs];
    }
  }
};
</script>
