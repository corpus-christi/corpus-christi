<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-text-field
          v-model="course.title"
          v-bind:label="$t('courses.title')"
          name="title"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('title')"
        ></v-text-field>

        <v-text-field
          v-model="course.description"
          v-bind:label="$t('courses.description')"
          name="description"
        ></v-text-field>
      </form>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="primary" flat v-on:click="cancel">
        {{ $t("actions.cancel") }}
      </v-btn>
      <v-btn color="primary" flat v-on:click="clear">
        {{ $t("actions.clear") }}
      </v-btn>
      <v-btn color="primary" flat v-on:click="save">
        {{ $t("actions.save") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { mapGetters } from "vuex";
import { isEmpty } from "lodash";

export default {
  name: "CourseForm",
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
    // List the keys in a Person record.
    courseKeys() {
      return Object.keys(this.course);
    },

    title() {
      return this.editMode
        ? this.$t("actions.edit")
        : this.$t("courses.new");
    },

    ...mapGetters(["currentLanguageCode"])
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
      this.$validator.reset();
    },

    // Trigger a save event, returning the update `Person`.
    save() {
      this.$validator.validateAll();
      if (!this.errors.any()) {
        this.$emit("save", this.course);
      }
    }
  }
};
</script>
