<template>
  <div>
    <v-text-field
      :label="$t(attribute.name)"
      :name="$t(attribute.name)"
      :value="attribute.value"
      @input="$emit('input', { stringValue: $event, enumValueId: 0 })"
      v-bind:error-messages="errors.collect(attribute.name)"
      v-validate="{ regex: /^[0-9]*$/ }"
    ></v-text-field>
  </div>
</template>

<script>
export default {
  name: "Integer",
  props: {
    attribute: {
      type: Object,
      required: true
    }
  }
};
</script>
