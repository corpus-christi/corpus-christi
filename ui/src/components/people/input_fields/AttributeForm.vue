<template>
  <div>
    <component
      v-for="(attribute, index) in attributes"
      :key="index"
      :is="attribute.type"
      @input="updateForm(attribute.id.toString(), index, $event)"
      v-bind:attribute="attribute"
    ></component>
  </div>
</template>

<script>
import store from "./../../../store.js";
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
  props: ["value", "existingAttributes", "personId"],
  data() {
    return {
      formData: this.value || {},
      attributes: [],
      translations: {}
    };
  },
  computed: {
    getCurrentLocaleCode() {
      return store.state.currentLocaleCode;
    }
  },
  watch: {
    existingAttributes() {
      if (this.existingAttributes && this.existingAttributes.length > 0) {
        for (let attr of this.attributes) {
          this.$set(
            attr,
            "value",
            this.getExistingAttribute(attr.id.toString())
          );
        }
      }
    },
    getCurrentLocaleCode() {
      this.getAllTranslations().then(() => {
        this.setupAttributes(this.attributes);
      });
    }
  },
  mounted() {
    Promise.all([this.getAttributesInfo(), this.getAllTranslations()]).then(
      () => {
        this.attributes.sort((a, b) => {
          return a.seq - b.seq;
        });
        this.setupAttributes(this.attributes);
      }
    );
  },
  methods: {
    getAttributesInfo() {
      return this.$http
        .get("/api/v1/people/persons/fields")
        .then(resp => {
          this.attributes = resp.data.person_attributes;
        })
        .catch(err => console.error("FAILURE", err));
    },

    getAllTranslations() {
      this.translations = {};
      return this.$http
        .get(`/api/v1/i18n/values/${store.state.currentLocaleCode}`)
        .then(resp => {
          for (let item of resp.data) {
            this.translations[item.key_id] = item.gloss;
          }
        })
        .catch(err => console.error("FAILURE", err.response));
    },

    getExistingAttribute(attributeId) {
      let idx = this.existingAttributes.findIndex(item => {
        return item.attributeId == attributeId;
      });
      let existingAttribute = this.existingAttributes[idx];
      return this.getStringOrEnumValue(existingAttribute);
    },

    getStringOrEnumValue(attr) {
      if (attr.stringValue) {
        return attr.stringValue;
      } else if (attr.enumValueId) {
        return attr.enumValueId;
      }
      return null;
    },

    setupAttributes(attributes) {
      for (let attr of attributes) {
        this.$set(attr, "name", this.translate(attr.nameI18n));
        this.$set(attr, "type", this.componentType(attr.typeI18n));
        this.$set(attr, "value", null);
        for (let enumval of attr.enumerated_values) {
          this.$set(enumval, "value", this.translate(enumval.valueI18n));
        }
        this.$set(this.formData, attr.id.toString(), {
          personId: this.personId ? this.personId : 0,
          attributeId: attr.id,
          enumValueId: 0,
          stringValue: ""
        });
      }
    },

    translate(key) {
      return this.translations[key]
        ? this.translations[key]
        : `No translation found for key ${key}`;
    },

    updateForm(attributeId, attributeIdx, value) {
      this.$set(this.formData, attributeId, {
        personId: this.personId ? this.personId : 0,
        attributeId: Number(attributeId),
        enumValueId: value.enumValueId,
        stringValue: value.stringValue
      });
      this.attributes[attributeIdx].value = this.getStringOrEnumValue(value);
      this.$emit("input", this.formData);
    },

    componentType(typeI18n) {
      switch (typeI18n) {
        case "attribute.float":
          return "Float";
        case "attribute.integer":
          return "Integer";
        case "attribute.date":
          return "Date";
        case "attribute.string":
          return "String";
        case "attribute.dropdown":
          return "Dropdown";
        case "attribute.checkbox":
          return "Check";
        case "attribute.radio":
          return "Radio";
      }
    },

    clear() {
      for (let idx in this.attributes) {
        this.$set(this.attributes[idx], "value", null);
        this.updateForm(this.attributes[idx].id.toString(), idx, {
          enumValueId: 0,
          stringValue: ""
        });
      }
    }
  }
};
</script>
