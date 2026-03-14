<template>
  <v-card>
    <v-card-title>
      <div>
        <h3 class="headline mb-0">
          {{ t("person.actions.add-participant") }}
        </h3>
      </div>
    </v-card-title>
    <v-card-text>
      <form><EntitySearch person v-model="newStudent" /></form>
    </v-card-text>

    <v-card-actions>
      <v-btn
        color="secondary"
        variant="text"
        :disabled="saving"
        v-on:click="cancel"
        data-cy="studentform-cancel"
        >{{ t("actions.cancel") }}
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        :disabled="Object.keys(newStudent).length == 0"
        :loading="saving"
        v-on:click="save"
        data-cy="studentform-save"
        >{{ t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { isEmpty } from "lodash";
import EntitySearch from "../EntitySearch.vue";

const { t } = useI18n();

const props = defineProps<{
  initialData: Record<string, any>;
  saving?: boolean;
}>();

const emit = defineEmits(["cancel", "save"]);

const newStudent = ref<Record<string, any>>({});

watch(() => props.initialData, (studentProp) => {
  if (isEmpty(studentProp)) {
    clear();
  } else {
    newStudent.value = studentProp;
  }
});

function cancel() {
  clear();
  emit("cancel");
}

function clear() {
  newStudent.value = {};
}

function save() {
  if (Object.keys(newStudent.value).length > 0) {
    emit("save", newStudent.value);
  }
}
</script>
