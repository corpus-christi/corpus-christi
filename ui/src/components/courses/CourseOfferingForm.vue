<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-combobox
          v-model="prereqs"
          :items="items"
          v-bind:label="$t('courses.title')"
          chips
          clearable
          solo
          multiple
        ></v-combobox>

        <!-- description -->
        <v-textarea
          v-model="course.description"
          v-bind:label="$t('courses.description')"
          name="description"
        ></v-textarea>

        <!-- date -->
        <v-layout row>
          <v-flex>
            <v-menu
              ref="menu"
              :close-on-content-click="false"
              v-model="menu"
              :nudge-right="40"
              :return-value.sync="dates"
              lazy
              transition="scale-transition"
              offset-y
              full-width
              min-width="290px"
            >
              <!-- TODO: Replace translations -->
              <v-combobox
                slot="activator"
                v-model="dates"
                multiple
                chips
                small-chips
                v-bind:label="$t('courses.title')"
                prepend-icon="event"
                readonly
              ></v-combobox>
              <v-date-picker v-model="dates" multiple no-title scrollable>
                <v-spacer></v-spacer>
                <v-btn flat color="primary" @click="menu = false">Cancel</v-btn>
                <v-btn flat color="primary" @click="$refs.menu.save(dates)">OK</v-btn>
              </v-date-picker>
            </v-menu>
          </v-flex>
        </v-layout>

        <!-- time -->
        <v-text-field v-model="course.name" v-bind:label="$t('courses.choose-time')" name="time"></v-text-field>

        <!-- teacher -->
        <v-text-field v-model="course.name" v-bind:label="$t('courses.choose-teacher')" name="location"></v-text-field>

        <!-- location -->
        <v-text-field v-model="course.name" v-bind:label="$t('courses.choose-location')" name="location"></v-text-field>

        <!-- max size -->
        <v-text-field
          v-model="course.description"
          v-bind:label="$t('courses.max-size')"
          name="description"
        ></v-text-field>
      </form>
    </v-card-text>
    <v-card-actions>
      <v-btn
        color="secondary"
        flat
        :disabled="saving"
        v-on:click="cancel"
      >{{ $t("actions.cancel") }}</v-btn>
      <v-spacer></v-spacer>
      <v-btn color="primary" flat :disabled="saving" v-on:click="clear">{{ $t("actions.clear") }}</v-btn>
      <v-btn
        color="primary"
        raised
        :disabled="saving"
        :loading="saving"
        v-on:click="save"
      >{{ $t("actions.save") }}</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>

import { isEmpty } from "lodash";

export default {
  name: "CourseOfferingForm",
  data: function() {
    return {
      availableCourses: [],
      prereqs: [],
      location: "location",
      teacher: "teacher",
      description: "description",
      time: "time",
      dates: [],
      menu: false,

      course: {}
    };
  },
  computed: {
    items() {
      return this.availableCourses.filter(item => item.id != this.course.id);
    },
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
  methods: {
     // Abandon ship.
    cancel() {
      this.clear();
      this.$emit("cancel");
    },

    // Clear the forms.
    clear() {
      this.course = {};
      this.$validator.reset();
    },

    // Trigger a save event, returning the updated `Course`.
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
  },
  mounted() {
    this.$http
      .get("/api/v1/courses/course-offering")
      .then(
        resp => (this.availableCourses = resp.data.filter(item => item.active))
      );
  }
};
</script>
