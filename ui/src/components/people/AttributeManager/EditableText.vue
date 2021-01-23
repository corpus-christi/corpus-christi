<template>
  <div>
    <v-text-field
      v-if="editMode"
      :value="value"
      @input="$emit('input', $event)"
      dense
    >
      <template v-slot:prepend>
        <v-icon v-if="draggable">drag_indicator</v-icon>
      </template>
    </v-text-field>
    <span v-else>
      {{ value }}
    </span>
  </div>
</template>

<script>
export default {
  name: "EditableText",

  props: {
    value: { type: String, default: "" },
    draggable: { type: Boolean, default: false },
    editMode: { type: Boolean, default: false },
  },
};
</script>
