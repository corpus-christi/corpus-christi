<template>
  <v-card>
    <v-card-title>
      <!-- <span class="headline">{{ hmm }}</span> -->
    </v-card-title>
    <v-card-text>
      <form>
        <!-- description -->
        <h2>TODO: Make this into a dropdown selection of all People</h2>
        <h3>ui/src/components/diplomas/DiplomaNewPersonForm.vue</h3>
        <!--
        <v-textarea
          v-model="courseOffering.description"
          v-bind:label="$t('courses.description')"
          name="description"
          rows="3"
          data-cy="course-offering-description"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('description')"
        ></v-textarea>

        <v-flex xs7 md7>
          <v-text-field
            v-model="courseOffering.maxSize"
            v-bind:label="$t('courses.max-size')"
            name="max-size"
            type="number"
            v-validate="'required'"
            v-bind:error-messages="errors.collect('max-size')"
            data-cy="course-offering-max-size"
          ></v-text-field>
        </v-flex>
        -->
      </form>
    </v-card-text>
    <v-card-actions>
      <v-btn color="secondary" text :disabled="saving" v-on:click="cancel">
        {{ $t("actions.cancel") }}
      </v-btn>
      <v-spacer></v-spacer>
      <!--
      <v-btn
        color="primary"
        raised
        :disabled="saving"
        :loading="saving"
        v-on:click="save"
        >{{ $t("actions.save") }}</v-btn
      >
      -->
    </v-card-actions>
  </v-card>
</template>

<script>
/**
 * This file was copied from ui/src/components/courses/CourseOfferingForm.vue
 */
import { isEmpty, cloneDeep } from "lodash";

export default {
  name: "DiplomaNewCourseForm",
  data: function () {
    return {
      saving: false,

      courseOffering: {},
    };
  },
  computed: {
    title() {
      return this.editMode
        ? this.$t("actions.edit")
        : this.$t("courses.new-offering");
    },
  },

  watch: {
    // Make sure data stays in sync with any changes to `initialData` from parent.
    initialData(courseProp) {
      if (isEmpty(courseProp)) {
        this.clear();
      } else {
        this.courseOffering = courseProp;
      }
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
    /*
    course: {
      type: Object,
      required: true,
    }, //*/
  },

  methods: {
    // Abandon ship.
    cancel() {
      this.clear();
      this.$emit("cancel");
    },

    // Clear the forms.
    clear() {
      this.courseOffering = {};
      this.$validator.reset();
    },

    // Save the record and trigger a save event, returning the updated `Course Offering`.
    save() {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          this.saving = true;
          let courseOffering = cloneDeep(this.courseOffering);
          courseOffering.courseId = this.course.id;
          this.saveCourseOffering(courseOffering);
        }
      });
    },

    saveCourseOffering(courseOffering) {
      if (this.editMode) {
        // Hang on to the ID of the record being updated.
        const courseOfferingId = courseOffering.id;

        // Get rid of the ID; not for consumption by endpoint.
        delete courseOffering.id;

        this.$http
          .patch(
            `/api/v1/courses/course_offerings/${courseOfferingId}`,
            courseOffering
          )
          .then((resp) => {
            console.log("EDITED", resp);
            courseOffering = resp.data;
            this.$emit("save", courseOffering);
          })
          .catch((err) => {
            console.error("FALURE", err.response);
            this.$emit("save", err);
          })
          .finally(() => {
            this.saving = false;
          });
      } else {
        courseOffering.active = true;
        this.$http
          .post("/api/v1/courses/course_offerings", courseOffering)
          .then((resp) => {
            console.log("ADDED", resp);
            courseOffering = resp.data;
            this.$emit("save", courseOffering);
          })
          .catch((err) => {
            console.error("FAILURE", err.response);
            this.$emit("save", err);
          })
          .finally(() => {
            this.saving = false;
          });
      }
    },
  },
};
</script>
