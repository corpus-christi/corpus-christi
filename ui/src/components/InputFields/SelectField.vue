<template>
  <v-select v-bind:label="label" :items="options">
  </v-select>
</template>

<script>
export default {
  name: "SelectField",
  props: {
    label: {
      type: String,
      required: true
    },
    options: {
      type: Array,
      required: true
    }
  }
};
</script>