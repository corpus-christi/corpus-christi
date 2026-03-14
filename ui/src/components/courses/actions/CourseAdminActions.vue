<template>
  <v-row align="center" justify="end" no-gutters>
    <v-tooltip location="bottom">
      <template #activator="{ props }">
        <v-btn
          variant="outlined"
          icon
          color="primary"
          v-bind="props"
          :size="displayContext === 'compact' ? 'small' : 'default'"
          @click="emitAction('edit')"
        >
          <v-icon :size="displayContext === 'compact' ? 'small' : 'default'">edit</v-icon>
        </v-btn>
      </template>
      <span>{{ t("actions.edit") }}</span>
    </v-tooltip>
    <v-tooltip location="bottom">
      <template #activator="{ props }">
        <v-btn
          variant="outlined"
          icon
          color="primary"
          v-bind="props"
          :size="displayContext === 'compact' ? 'small' : 'default'"
          @click="emitAction(course.active ? 'deactivate' : 'activate')"
        >
          <v-icon :size="displayContext === 'compact' ? 'small' : 'default'">
            {{ course.active ? "archive" : "undo" }}
          </v-icon>
        </v-btn>
      </template>
      <span>{{
        t(
          course.active
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
  course: Record<string, any>;
  displayContext?: string;
}>();

const emit = defineEmits(["action"]);

function emitAction(actionName: string) {
  emit("action", actionName);
}
</script>

<style></style>
