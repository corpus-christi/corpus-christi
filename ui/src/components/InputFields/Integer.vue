<template>
  <v-text-field
    :label="label"
    :name="name"
    :value="value"
    @input="$emit('input', $event)"
    v-validate="'decimal:0'"
  ></v-text-field>
</template>

<script>
export default {
  name: "Integer",
  props: {
    label: {
      type: String,
      required: true
    },
    name: {
      type: String,
      required: true
    },
    value: {
      type: String,
      required: true
    }
  }
};
</script>
