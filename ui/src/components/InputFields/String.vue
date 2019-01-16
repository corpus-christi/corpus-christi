<template>
  <v-text-field v-bind:label="label"></v-text-field>
</template>

<script>
export default {
  name: "String",
  props: {
    label: {
      type: String,
      required: true
    }
  }
};
</script>
