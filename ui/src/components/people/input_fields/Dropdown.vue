<template>
  <div>
    <v-select
      :label="t(attribute.name)"
      :name="t(attribute.name)"
      :model-value="attribute.value"
      @update:model-value="emit('input', { stringValue: '', enumValueId: $event })"
      :items="getItems"
    ></v-select>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  attribute: any;
}>();

const emit = defineEmits(["input"]);

const getItems = computed(() => {
  let items: any[] = [];
  for (let enumeratedValue of props.attribute.enumerated_values) {
    items.push({
      title: t(enumeratedValue.value),
      value: enumeratedValue.id
    });
  }
  return items;
});
</script>
