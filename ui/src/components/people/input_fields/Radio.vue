<template>
  <v-container>
    <span class="title">{{ t(attribute.name) }}</span>
    <v-radio-group
      :model-value="attribute.value"
      @update:model-value="emit('input', { stringValue: '', enumValueId: $event })"
    >
      <v-radio
        v-for="(enumerateValue, index) in attribute.enumerated_values"
        :key="index"
        :label="t(enumerateValue.value)"
        :name="t(enumerateValue.value)"
        :value="enumerateValue.id"
      ></v-radio>
    </v-radio-group>
  </v-container>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  attribute: any;
}>();

const emit = defineEmits(["input"]);
</script>
