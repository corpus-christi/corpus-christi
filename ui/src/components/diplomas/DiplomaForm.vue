<template>
  <form>
    <v-text-field
      v-model="diploma.title"
      v-bind:label="$t('diplomas.title')"
      name="title"
      v-validate="'required'"
      v-bind:error-messages="errors.collect('title')"
    ></v-text-field>

    <v-text-field
      v-model="diploma.description"
      v-bind:label="$t('diplomas.description')"
      name="description"
    ></v-text-field>
    <!-- translate prereq -->
    <v-combobox
      v-model="prereqs"
      :items="items"
      v-bind:label="$t('diplomas.prerequisites')"
      chips
      clearable
      solo
      multiple
    >
      <template slot="item" slot-scope="data">{{data.item.title}}</template>
      <template slot="selection" slot-scope="data">
        <v-chip :selected="data.selected" close @input="remove(data.item)">
          <strong>{{ data.item.title }}</strong>&nbsp;
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
      allDiplomas: [],
      prereqs: []
    };
  },
  computed: {
    items() {
      return this.allDiplomas.filter(item => item.id != this.diploma.id);
    }
  },
  props: {
    diploma: Object
	},
	methods: {
    remove(item) {
      this.prereqs.splice(this.prereqs.indexOf(item), 1);
      this.prereqs = [...this.prereqs];
    }
	},
  mounted() {
    this.$http
      .get("/api/v1/courses/diplomas")
      .then(resp => (this.allDiplomas = resp.data));
  }
};
</script>