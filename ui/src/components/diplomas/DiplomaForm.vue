<template>
  <form>
    <v-text-field
      v-model="diploma.name"
      v-bind:label="$t('diplomas.title')"
      name="name"
      v-validate="'required'"
      v-bind:error-messages="errors.collect('name')"
    ></v-text-field>

    <v-text-field
      v-model="diploma.description"
      v-bind:label="$t('diplomas.description')"
      name="description"
    ></v-text-field>
    <!-- translate courses -->
    <v-combobox
      v-model="diploma.courses"
      :items="items"
      v-bind:label="$t('diplomas.courses')"
      hide-selected 
      item-value = "id"
      chips
      clearable
      solo
      multiple
    >
      <template slot="item" slot-scope="data">{{data.item.name}}</template>
      <template slot="selection" slot-scope="data">
        <v-chip :selected="data.selected" close @input="remove(data.item)">
          <strong>{{ data.item.name }}</strong>&nbsp;
        </v-chip>
      </template>
    </v-combobox>
  </form>
</template>

<script>
export default {
  name: "DiplomaForm",
  data: function() {
    return {
      //allDiplomas: [],  // all diplomas
      allCourses: [],   // all courses (the list from which courses can be chosen)
      diplomaCourses: []  // courses for this diploma (the list of courses for this diploma)
    };
  },

  computed: {
    items() {
      return this.allCourses;
    }


  },
  props: {
    diploma: Object
	},
	methods: {
    remove(item) {
      // remove a course from the list of courses for this diploma
      this.diplomaCourses.splice(this.diplomaCourses.indexOf(item), 1);
      this.diplomaCourses = [...this.diplomaCourses];
    }
  },
  mounted() {
    this.$http
      .get("/api/v1/courses/courses")
      .then(resp => (this.allCourses = resp.data));
  }
};
</script>