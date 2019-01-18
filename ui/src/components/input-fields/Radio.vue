<template>
  <v-container>
    <span class="title">{{ attribute.name }}</span>
    <v-radio-group row :value="attribute.value" @change="$emit('input', { stringValue: '', enumValueId: $event})">
      <v-radio
        v-for="(enumerateValue, index) in attribute.enumerated_values"
        :key="index"
        :label="enumerateValue.value"
        :name="enumerateValue.value"
        :value="enumerateValue.id"
      ></v-radio>
    </v-radio-group>
  </v-container>
</template>

<script>
export default {
  name: "Radio",
  props: {
    attribute: {
      type: Object,
      required: true
    }
  }
};
</script>
