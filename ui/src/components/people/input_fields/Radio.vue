<template>
  <v-container>
    <span class="title">{{ label }}</span>
    <v-radio-group row :value="value" @change="$emit('input', $event)">
      <v-radio
        v-for="(option, index) in options"
        :key="index"
        :label="option.label"
        :name="option.name"
        :value="option.value"
      ></v-radio>
    </v-radio-group>
  </v-container>
</template>

<script>
export default {
  name: "Radio",
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
      type: Number,
      required: true
    }
  }
};
</script>
