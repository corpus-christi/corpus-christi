<template>
  <form>
    <v-text-field
      v-model="course.name"
      v-bind:label="$t('courses.title')"
      name="name"
      v-validate="'required'"
      v-bind:error-messages="errors.collect('name')"
    ></v-text-field>

    <v-text-field
      v-model="course.description"
      v-bind:label="$t('courses.description')"
      name="description"
    ></v-text-field>
    <!-- translate prereq -->
    <v-combobox
      v-model="prereqs"
      :items="items"
      v-bind:label="$t('courses.prerequisites')"
      chips
      clearable
      solo
      multiple
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
      availableCourses: [],
      prereqs: []
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
      this.prereqs.splice(this.prereqs.indexOf(item), 1);
      this.prereqs = [...this.prereqs];
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
