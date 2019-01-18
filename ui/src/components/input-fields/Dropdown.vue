<template>
  <div>
    <v-select
      :label="attribute.name"
      :name="attribute.name"
      :value="attribute.value"
      @input="$emit('input', { stringValue: '', enumValueId: $event})"
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
        let items = []
        for(let enumeratedValue of this.attribute.enumerated_values) {
          items.push({
            text: enumeratedValue.value,
            value: enumeratedValue.id
          });
        }
        return items
      }
  }
};
</script>