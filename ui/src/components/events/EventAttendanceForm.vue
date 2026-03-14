<template>
  <v-card>
    <v-card-text>
      <span class="headline">{{ t("events.attendance") }}</span>
      <v-text-field
        data-cy="attendance-input"
        name="attendance"
        type="number"
        v-model="number"
        :placeholder="t('events.attendance-label')"
        :error-messages="attendanceErrors"
      ></v-text-field>
    </v-card-text>
    <v-card-actions>
      <v-btn
        color="secondary"
        variant="text"
        v-on:click="$emit('cancel')"
        :disabled="saving"
        data-cy="attendance-cancel"
        >{{ t("actions.cancel") }}</v-btn
      >
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        v-on:click="changeAttendance"
        :loading="saving"
        data-cy="attendance-save"
        >{{ t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  attendance: any;
  saving: boolean;
}>();

const emit = defineEmits(["cancel", "save-attendance"]);

const number = ref<any>(null);
const attendanceErrors = ref<string[]>([]);

watch(() => props.attendance, (val) => {
  number.value = val;
});

function changeAttendance() {
  attendanceErrors.value = [];
  if (number.value === null || number.value === "") {
    attendanceErrors.value = [t("validations.required")];
    return;
  }
  const num = parseInt(number.value);
  if (isNaN(num) || num < 0) {
    attendanceErrors.value = [t("validations.integer")];
    return;
  }
  emit("save-attendance", num);
}
</script>
