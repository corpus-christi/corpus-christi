<template>
  <v-card>
    <v-card-title data-cy="course-editor-title">
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text> <CourseForm ref="form" :course="course" /> </v-card-text>
    <v-card-actions data-cy="course-editor-actions">
      <v-btn color="secondary" flat :disabled="saving" v-on:click="cancel">
        {{ $t("actions.cancel") }}
      </v-btn>
      <v-spacer></v-spacer>
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
    }
  },
  data: function() {
    return {
      course: {},
      saving: false
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
      this.$refs.form.$validator.validateAll().then(() => {
        if (!this.$refs.form.errors.any()) {
          this.saving = true;
          let course = cloneDeep(this.course);
          this.saveCourse(course);
        }
      });
    },

    saveCourse(course) {
      let courseAttrs = {
        description: course.description,
        name: course.name
      };

      if (this.editMode) {
        let promises = [];
        promises.push(
          this.$http
            .patch(`/api/v1/courses/courses/${course.id}`, courseAttrs)
            .then(resp => {
              console.log("EDITED", resp);
              return resp;
            })
        );
        promises.push(
          this.$http.patch(
            `/api/v1/courses/courses/${course.id}/prerequisites`,
            { prerequisites: course.prerequisites.map(prereq => prereq.id) } // API expects array of IDs
          )
        );

        Promise.all(promises)
          .then(resps => {
            let newCourse = resps[0].data;
            newCourse.prerequisites = course.prerequisites; // Re-attach prereqs so they show up in UI
            this.$emit("save", newCourse);
          })
          .catch(err => {
            console.error("FALURE", err.response);
            this.$emit("save", err);
          })
          .finally(() => {
            this.saving = false;
          });
      } else {
        // All new courses are active
        courseAttrs.active = true;
        let newCourse;
        this.$http
          .post("/api/v1/courses/courses", courseAttrs)
          .then(resp => {
            console.log("ADDED", resp);
            newCourse = resp.data;
            newCourse.prerequisites = course.prerequisites; // Re-attach prereqs so they show up in UI

            // Now that course created, add prerequisites to it
            return this.$http.patch(
              `/api/v1/courses/courses/${newCourse.id}/prerequisites`,
              { prerequisites: course.prerequisites.map(prereq => prereq.id) } // API expects array of IDs
            );
          })
          .then(resp => {
            console.log("PREREQS", resp);
            this.$emit("save", newCourse);
          })
          .catch(err => {
            console.error("FAILURE", err);
            this.$emit("save", err);
          })
          .finally(() => {
            this.saving = false;
          });
      }
    }
  }
};
</script>
