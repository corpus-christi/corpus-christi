<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-textarea
          rows="3"
          v-model="team.description"
          v-bind:label="t('teams.description')"
          name="team-description"
          data-cy="description"
        ></v-textarea>
      </form>
    </v-card-text>
    <v-card-actions>
      <v-btn
        color="secondary"
        variant="text"
        v-on:click="cancel"
        :disabled="formDisabled"
        data-cy="form-cancel"
        >{{ t("actions.cancel") }}</v-btn
      >
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        variant="outlined"
        v-on:click="addAnother"
        v-if="!props.editMode"
        :loading="props.addMoreLoading"
        :disabled="formDisabled"
        data-cy="form-addanother"
        >{{ t("actions.add-another") }}</v-btn
      >
      <v-btn
        color="primary"
        variant="elevated"
        v-on:click="save"
        :loading="props.saveLoading"
        :disabled="formDisabled"
        data-cy="form-save"
        >{{ t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useI18n } from "vue-i18n";
import { isEmpty } from "lodash";

const { t } = useI18n();

const props = defineProps<{
  editMode: boolean;
  initialData: Record<string, any>;
  saveLoading?: boolean;
  addMoreLoading?: boolean;
}>();

const emit = defineEmits(["cancel", "save", "addAnother"]);

const team = ref<Record<string, any>>({});
const addMore = ref(false);

const title = computed(() => {
  return props.editMode ? t("teams.edit-team") : t("teams.create-team");
});

const formDisabled = computed(() => {
  return props.saveLoading || props.addMoreLoading;
});

watch(
  () => props.initialData,
  (teamProp) => {
    if (isEmpty(teamProp)) {
      clear();
    } else {
      team.value = teamProp;
    }
  }
);

function cancel() {
  emit("cancel");
}

function clear() {
  for (let key of Object.keys(team.value)) {
    team.value[key] = "";
  }
}

function addAnother() {
  addMore.value = true;
  save();
}

function save() {
  team.value.active = true;
  if (addMore.value) {
    emit("addAnother", team.value);
  } else {
    emit("save", team.value);
  }
  addMore.value = false;
}
</script>
