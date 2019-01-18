<template>
  <div>
    <component
      v-for="(field, index) in attributes"
      :key="index"
      :is="field.fieldType"
      :value="formData[field.name]"
      @input="updateForm(field.name, $event)"
      v-bind="field"
    >
    </component>
  </div>
</template>

<script>
import String from "./String.vue";
import Dropdown from "./Dropdown.vue";
export default {
  name: "AttributeForm",
  components: { String, Dropdown },
  props: ["attributes", "value"],
  data() {
    return {
      formData: this.value || {}
    };
  },
  methods: {
    updateForm(fieldName, value) {
      this.$set(this.formData, fieldName, value);
      this.$emit("input", this.formData);
    }
  }
};
</script>
