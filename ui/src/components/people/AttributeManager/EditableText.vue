<template>
  <div>
    <v-text-field
      v-if="editMode"
      :value="value"
      @input="$emit('value', $event)"
      dense
    />
    <span v-else>{{ value }}</span>
  </div>
</template>

<script>
export default {
  name: "EditableText",

  props: {
    value: { type: String, default: "" },
    editMode: { type: Boolean, default: false },
  },
};
</script>
