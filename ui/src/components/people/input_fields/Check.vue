<template>
  <v-container>
    <span class="title">{{ t(attribute.name) }}</span>
    <v-row>
      <v-checkbox
        v-for="(enumeratedValue, index) in attribute.enumerated_values"
        :key="index"
        :label="t(enumeratedValue.value)"
        :name="t(enumeratedValue.value)"
        :value="enumeratedValue.id"
        v-model="selected"
        @update:model-value="emit('input', { stringValue: selected.toString(), enumValueId: 0 })"
      ></v-checkbox>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  attribute: any;
}>();

const emit = defineEmits(["input"]);

const selected = ref<any[]>([]);

const getAttributeValue = computed(() => props.attribute.value);

watch(getAttributeValue, () => {
  if (props.attribute.value) {
    let value = props.attribute.value.split(",");
    for (let index in value) {
      value[index] = Number(value[index]);
    }
    selected.value = value;
  } else {
    selected.value = [];
  }
});
</script>
