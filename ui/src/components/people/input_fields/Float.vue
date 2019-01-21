<template>
  <v-text-field
    :label="label"
    :name="name"
    :value="value"
    @input="$emit('input', $event)"
    v-bind:error-messages="errors.collect(name)"
    v-validate="{ regex: /^[0-9]*(\.[0-9]+)?$/ }"
  ></v-text-field>
</template>

<script>
export default {
  name: "Float",
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
