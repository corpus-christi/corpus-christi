<template>
  <div>
    <v-text-field
      :label="t(attribute.name)"
      :name="t(attribute.name)"
      :model-value="attribute.value"
      @update:model-value="emit('input', { stringValue: $event, enumValueId: 0 })"
    ></v-text-field>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  attribute: any;
}>();

const emit = defineEmits(["input"]);
</script>
