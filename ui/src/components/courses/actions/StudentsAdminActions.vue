<template>
  <v-row align="center" justify="end" no-gutters>
    <v-tooltip location="bottom" v-if="!student.confirmed">
      <template #activator="{ props }">
        <v-btn
          variant="outlined"
          icon
          color="primary"
          v-bind="props"
          :size="displayContext === 'compact' ? 'small' : 'default'"
          @click="emitAction('confirm')"
        >
          <v-icon :size="displayContext === 'compact' ? 'small' : 'default'">done</v-icon>
        </v-btn>
      </template>
      <span>{{ t("actions.confirm") }}</span>
    </v-tooltip>
    <v-tooltip location="bottom">
      <template #activator="{ props }">
        <v-btn
          variant="outlined"
          icon
          color="primary"
          v-bind="props"
          :size="displayContext === 'compact' ? 'small' : 'default'"
          @click="emitAction(student.active ? 'deactivate' : 'activate')"
        >
          <v-icon :size="displayContext === 'compact' ? 'small' : 'default'">
            {{ student.active ? "archive" : "undo" }}
          </v-icon>
        </v-btn>
      </template>
      <span>{{
        t(
          student.active
            ? "actions.tooltips.archive"
            : "actions.tooltips.unarchive"
        )
      }}</span>
    </v-tooltip>
  </v-row>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  student: Record<string, any>;
  displayContext?: string;
}>();

const emit = defineEmits(["action"]);

function emitAction(actionName: string) {
  emit("action", actionName);
}
</script>

<style></style>
