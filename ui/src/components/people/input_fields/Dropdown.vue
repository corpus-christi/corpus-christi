<template>
  <div>
    <v-select
      :label="$t(attribute.name)"
      :name="$t(attribute.name)"
      :value="attribute.value"
      @input="$emit('input', { stringValue: '', enumValueId: $event })"
      :items="getItems"
    ></v-select>
  </div>
</template>

<script>
export default {
  name: "Dropdown",
  props: {
    attribute: {
      type: Object,
      required: true
    }
  },
  computed: {
    getItems() {
      let items = [];
      for (let enumeratedValue of this.attribute.enumerated_values) {
        items.push({
          text: this.$t(enumeratedValue.value),
          value: enumeratedValue.id
        });
      }
      return items;
    }
  }
};
</script>
