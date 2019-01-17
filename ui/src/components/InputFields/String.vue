<template>
  <v-text-field
    :label="label"
    :name="name"
    :value="value"
    @input="$emit('input', $event)"
    v-validate="{regex: '^[a-zA-Z]*$'}"
  ></v-text-field>
</template>

<script>
export default {
  name: "String",
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
