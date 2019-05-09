<template>
  <v-card>
    <v-card-title data-cy="course-form-title">
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-layout align-space-around justify-center column fill-height>
          <v-flex>
            <v-text-field
              v-model="course.name"
              v-bind:label="$t('courses.title')"
              name="title"
              v-validate="'required'"
              v-bind:error-messages="errors.collect('title')"
              data-cy="course-form-name"
            ></v-text-field>
          </v-flex>
          <v-flex>
            <v-textarea
              v-model="course.description"
              v-bind:label="$t('courses.description')"
              name="description"
              v-validate="'required'"
              v-bind:error-messages="errors.collect('description')"
              data-cy="course-form-description"
            ></v-textarea>
          </v-flex>
          <v-btn
            class="text-xs-center"
            color="primary"
            flat
            small
            @click="showImageChooser = true"
            :disabled="showImageChooser"
          >
            {{ $t("images.actions.add-image") }}
          </v-btn>
          <v-flex>
            <v-expand-transition>
              <image-chooser
                v-if="showImageChooser"
                :imageId="getImageId"
                v-on:saved="chooseImage"
                v-on:deleted="deleteImage"
                v-on:cancel="cancelImageChooser"
                v-on:missing="missingImage"
              />
            </v-expand-transition>
          </v-flex>
          <br />
          <v-flex>
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
              data-cy="course-form-prerequisites"
            >
            </v-select>
          </v-flex>
        </v-layout>
      </form>
    </v-card-text>
    <v-card-actions data-cy="course-form-actions">
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
import ImageChooser from "../images/ImageChooser";

export default {
  name: "CourseForm",
  components: { "image-chooser": ImageChooser },
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
      addMore: false,
      imageSaved: false,
      showImageChooser: false
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
      return (
        this.saveLoading ||
        this.addMoreLoading ||
        (this.showImageChooser && !this.imageSaved)
      );
    },

    getImageId() {
      if (this.course.images) {
        return this.course.images.length > 0
          ? this.course.images[0].image_id
          : -1;
      } else {
        return -1;
      }
    }
  },

  watch: {
    // Make sure data stays in sync with any changes to `initialData` from parent.
    initialData(courseProp) {
      console.log(courseProp);
      if (isEmpty(courseProp)) {
        this.clear();
      } else {
        this.course = courseProp;
        if (this.course.images && this.course.images.length > 0) {
          this.showImageChooser = true;
          this.imageSaved = true;
        } else {
          this.showImageChooser = false;
          this.imageSaved = false;
        }
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
      this.showImageChooser = false;
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
    },

    chooseImage(id) {
      this.course.newImageId = id;
      this.imageSaved = true;
    },

    deleteImage() {
      this.showImageChooser = false;
      delete this.course.newImageId;
      this.course.images = [];
      this.imageSaved = false;
    },

    cancelImageChooser() {
      this.showImageChooser = false;
    },

    missingImage() {
      this.imageSaved = false;
    }
  },

  mounted() {
    this.loadCoursesPool();
  }
};
</script>
