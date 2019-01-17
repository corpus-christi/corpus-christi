<template>
  <div>
    <component
      v-for="(attribute, index) in attributes"
      :key="index"
      :is="attribute.fieldType"
      :value="formData[attribute.name]"
      @input="updateForm(attribute.name, $event)"
      v-bind="attribute"
    >
    </component>
  </div>
</template>

<script>
import Date from "./Date.vue";
import Float from "./Float.vue";
import Integer from "./Integer.vue";
import String from "./String.vue";
import Dropdown from "./Dropdown.vue";
import Check from "./Check.vue";
import Radio from "./Radio.vue";

export default {
  name: "AttributeForm",
  components: { Date, Float, Integer, String, Dropdown, Check, Radio },
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
