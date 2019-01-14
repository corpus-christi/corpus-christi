<template>
  <form>
    <v-text-field
      v-model="course.name"
      v-bind:label="$t('courses.title')"
      name="title"
      v-validate="'required'"
      v-bind:error-messages="errors.collect('title')"
      data-cy="course-form-name"
    ></v-text-field>

    <v-textarea
      v-model="course.description"
      v-bind:label="$t('courses.description')"
      name="description"
      data-cy="course-form-description"
    ></v-textarea>

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
  </form>
</template>

<script>
export default {
  name: "CourseForm",
  computed: {
    items() {
      return this.coursesPool.filter(item => item.active && item.id != this.course.id);
    },
  },
  props: {
    course: Object,
    coursesPool: Array
  }
};
</script>
