<template>
  <v-card>
    <v-card-title data-cy="title">
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-text-field
          v-model="course.name"
          v-bind:label="$t('courses.title')"
          name="title"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('title')"
          data-cy="name"
        ></v-text-field>

        <v-textarea
          v-model="course.description"
          v-bind:label="$t('courses.description')"
          name="description"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('description')"
          data-cy="description"
        ></v-textarea>
        <br />
        <div data-cy="prerequisites">
        <v-select
          v-model="course.prerequisites"
          :items="items"
          v-bind:label="$t('courses.prerequisites')"
          chips
          deletable-chips
          clearable
          outline
          multiple
          hide-selected
          return-object
          item-value="id"
          item-text="name"
          :menu-props="{ closeOnContentClick: true }"
        >
        </v-select>
        </div>
      </form>
    </v-card-text>
    <v-card-actions data-cy="actions">
      <v-btn
        color="secondary"
        flat
        :disabled="formDisabled"
        v-on:click="cancel"
        data-cy="cancel"
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
        data-cy="save"
      >
        {{ $t("actions.save") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { isEmpty, cloneDeep } from "lodash";

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
    },
    courses: {
      type: Array
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
      coursesPool: [],
      addMore: false
    };
  },
  computed: {
    items() {
      return this.coursesPool.filter(
        item => item.active && item.id != this.course.id
      );
    },
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
    },
    courses: "loadCoursesPool"
  },

  methods: {
    // Abandon ship.
    cancel() {
      this.$emit("cancel");
    },

    // Clear the forms.
    clear() {
      this.course = {};
      this.$validator.reset();
    },

    addAnother() {
      this.addMore = true;
      this.save();
    },

    save() {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          let course = cloneDeep(this.course);
          if (this.addMore) this.$emit("addAnother", course);
          else this.$emit("save", course);
        }
        this.addMore = false;
      });
    },

    loadCoursesPool() {
      if (!this.courses) {
        this.loading = true;
        this.$http.get(`/api/v1/courses/courses`).then(resp => {
          this.coursesPool = resp.data;
          this.loading = false;
        });
      } else {
        this.coursesPool = this.courses;
      }
    }
  },

  mounted() {
    this.loadCoursesPool();
  }
};
</script>
