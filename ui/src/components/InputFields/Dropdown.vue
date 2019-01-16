<template>
  <v-select
    :label="label"
    :name="name"
    :value="value"
    @input="$emit('input', $event)"
    :items="options"
  >
  </v-select>
</template>

<script>
export default {
  name: "Dropdown",
  props: {
    label: {
      type: String,
      required: true
    },
    options: {
      type: Array,
      required: true
    },
    name: {
      type: String,
      required: true
    },
    value: {
      type: Number,
      required: true
    }
  }
};
</script>
