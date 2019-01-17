<template>
  <v-container>
    <span class="title">{{ label }}</span>
    <v-layout row>
      <v-checkbox
        v-for="(field, index) in options"
        :key="index"
        :label="field.label"
        :name="field.name"
        :value="field.value"
        v-model="selected"
        @change="$emit('input', selected)"
      ></v-checkbox>
    </v-layout>
  </v-container>
</template>

<script>
export default {
  name: "Check",
  props: {
    options: {
      type: Array,
      required: true
    },
    label: {
      type: String,
      required: true
    },
    name: {
      type: String,
      required: true
    },
    value: {
      type: Array,
      required: false
    }
  },
  data() {
    return {
      selected: []
    };
  },

  watch: {
    value(val) {
      this.selected = val;
    }
  }
};
</script>
