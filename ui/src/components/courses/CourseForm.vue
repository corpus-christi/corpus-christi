<template>
  <form>
    <v-text-field
      v-model="course.name"
      v-bind:label="$t('courses.title')"
      name="title"
      v-validate="'required'"
      v-bind:error-messages="errors.collect('title')"
    ></v-text-field>

    <v-textarea
      v-model="course.description"
      v-bind:label="$t('courses.description')"
      name="description"
    ></v-textarea>
    <!-- translate prereq -->
    <v-combobox
      v-model="course.prerequisites"
      :items="items"
      v-bind:label="$t('courses.prerequisites')"
      chips
      clearable
      solo
      multiple
      hide-selected
      item-value="id"
    >
      <template slot="item" slot-scope="data">{{ data.item.name }}</template>
      <template slot="selection" slot-scope="data">
        <v-chip :selected="data.selected" close @input="remove(data.item)">
          <strong>{{ data.item.name }}</strong
          >&nbsp;
        </v-chip>
      </template>
    </v-combobox>
  </form>
</template>

<script>
export default {
  name: "CourseForm",
  data: function() {
    return {
      availableCourses: []
    };
  },
  computed: {
    items() {
      return this.availableCourses.filter(item => item.id != this.course.id);
    }
  },
  props: {
    course: Object
  },
  methods: {
    remove(item) {
      this.course.prerequisites.splice(this.course.prerequisites.indexOf(item), 1);
      this.course.prerequisites = [...this.course.prerequisites];
    }
  },
  mounted() {
    this.$http
      .get("/api/v1/courses/courses")
      .then(
        resp => (this.availableCourses = resp.data.filter(item => item.active))
      );
  }
};
</script>
