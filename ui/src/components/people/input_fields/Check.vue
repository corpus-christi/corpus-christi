<template>
  <v-container>
    <span class="title">{{ $t(attribute.name) }}</span>
    <v-layout row>
      <v-checkbox
        v-for="(enumeratedValue, index) in attribute.enumerated_values"
        :key="index"
        :label="$t(enumeratedValue.value)"
        :name="$t(enumeratedValue.value)"
        :value="enumeratedValue.id"
        v-model="selected"
        @change="
          $emit('input', { stringValue: selected.toString(), enumValueId: 0 })
        "
      ></v-checkbox>
    </v-layout>
  </v-container>
</template>

<script>
export default {
  name: "Check",
  props: {
    attribute: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      selected: []
    };
  },
  computed: {
    getAttributeValue() {
      return this.attribute.value;
    }
  },
  watch: {
    getAttributeValue() {
      if (this.attribute.value) {
        let value = this.attribute.value.split(",");
        for (let index in value) {
          value[index] = Number(value[index]);
        }
        this.selected = value;
      } else {
        this.selected = [];
      }
    }
  }
};
</script>
