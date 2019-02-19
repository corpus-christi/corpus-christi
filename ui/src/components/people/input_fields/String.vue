<template>
  <div>
    <v-text-field
      :label="$t(attribute.name)"
      :name="$t(attribute.name)"
      :value="attribute.value"
      @input="$emit('input', { stringValue: $event, enumValueId: 0 })"
    ></v-text-field>
  </div>
</template>

<script>
export default {
  name: "String",
  props: {
    attribute: {
      type: Object,
      required: true
    }
  }
};
</script>
