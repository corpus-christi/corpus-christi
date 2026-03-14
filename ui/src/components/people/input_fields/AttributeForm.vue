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

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import DateField from "./Date.vue";
import Float from "./Float.vue";
import Integer from "./Integer.vue";
import StringField from "./String.vue";
import Dropdown from "./Dropdown.vue";
import Check from "./Check.vue";
import Radio from "./Radio.vue";

const http = inject<AxiosInstance>("$http")!;

const props = defineProps<{
  modelValue?: any;
  existingAttributes?: any[];
  personId?: any;
}>();

const emit = defineEmits(["input", "update:modelValue"]);

const formData = ref<any>(props.modelValue || {});
const attributes = ref<any[]>([]);

watch(
  () => props.existingAttributes,
  () => {
    if (props.existingAttributes && props.existingAttributes.length > 0) {
      for (let attr of attributes.value) {
        attr.value = getExistingAttribute(attr.id.toString());
      }
    }
  }
);

function getAttributesInfo() {
  return http
    .get("/api/v1/people/persons/fields")
    .then(resp => {
      attributes.value = resp.data.person_attributes;
    })
    .catch(err => console.error("FAILURE", err));
}

function getExistingAttribute(attributeId: string) {
  if (!props.existingAttributes) return null;
  let idx = props.existingAttributes.findIndex(item => {
    return item.attributeId == attributeId;
  });
  let existingAttribute = props.existingAttributes[idx];
  return getStringOrEnumValue(existingAttribute);
}

function getStringOrEnumValue(attr: any) {
  if (attr.stringValue) {
    return attr.stringValue;
  } else if (attr.enumValueId) {
    return attr.enumValueId;
  }
  return null;
}

function setupAttributes(attrs: any[]) {
  for (let attr of attrs) {
    attr.name = attr.nameI18n;
    attr.type = componentType(attr.typeI18n);
    attr.value = null;
    for (let enumval of attr.enumerated_values) {
      enumval.value = enumval.valueI18n;
    }
    formData.value[attr.id.toString()] = {
      personId: props.personId ? props.personId : 0,
      attributeId: attr.id,
      enumValueId: 0,
      stringValue: ""
    };
  }
}

function updateForm(attributeId: string, attributeIdx: number, value: any) {
  formData.value[attributeId] = {
    personId: props.personId ? props.personId : 0,
    attributeId: Number(attributeId),
    enumValueId: value.enumValueId,
    stringValue: value.stringValue
  };
  attributes.value[attributeIdx].value = getStringOrEnumValue(value);
  emit("input", formData.value);
  emit("update:modelValue", formData.value);
}

function componentType(typeI18n: string) {
  switch (typeI18n) {
    case "attribute.float":
      return Float;
    case "attribute.integer":
      return Integer;
    case "attribute.date":
      return DateField;
    case "attribute.string":
      return StringField;
    case "attribute.dropdown":
      return Dropdown;
    case "attribute.checkbox":
      return Check;
    case "attribute.radio":
      return Radio;
  }
}

function clear() {
  for (let idx in attributes.value) {
    attributes.value[idx].value = null;
    updateForm(attributes.value[idx].id.toString(), Number(idx), {
      enumValueId: 0,
      stringValue: ""
    });
  }
}

defineExpose({ clear });

onMounted(() => {
  getAttributesInfo().then(() => {
    attributes.value.sort((a, b) => {
      return a.seq - b.seq;
    });
    setupAttributes(attributes.value);
  });
});
</script>
