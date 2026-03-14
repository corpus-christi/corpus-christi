<template>
  <div>
    <v-menu
      :close-on-content-click="false"
      v-model="showDatePicker"
      :nudge-right="40"
      transition="scale-transition"
      offset-y
      min-width="290px"
    >
      <template #activator="{ props: menuProps }">
        <v-text-field
          v-bind="menuProps"
          prepend-icon="event"
          readonly
          :label="t(attribute.name)"
          :name="t(attribute.name)"
          :model-value="attribute.value"
        ></v-text-field>
      </template>

      <v-date-picker
        :model-value="attribute.value"
        @update:model-value="
          showDatePicker = false;
          emit('input', { stringValue: $event, enumValueId: 0 });
        "
      ></v-date-picker>
    </v-menu>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  attribute: any;
}>();

const emit = defineEmits(["input"]);

const showDatePicker = ref(false);
</script>
