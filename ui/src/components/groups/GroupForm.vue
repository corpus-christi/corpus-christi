<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ name }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-text-field
          v-model="group.name"
          v-bind:label="t('groups.name')"
          name="title"
          data-cy="title"
        />
        <v-textarea
          rows="3"
          v-model="group.description"
          v-bind:label="t('groups.group-description')"
          name="description"
          data-cy="description"
        />
        <entity-search
          manager
          :value="manager"
          @input="updateSelection"
          name="manager"
        />
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
      <v-spacer />
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

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false" data-cy>
          {{ t("actions.close") }}
        </v-btn>
      </template>
    </v-snackbar>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import { isEmpty } from "lodash";
import EntitySearch from "../EntitySearch.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;

const props = defineProps<{
  editMode: boolean;
  initialData: Record<string, any>;
  saveLoading?: boolean;
  addMoreLoading?: boolean;
}>();

const emit = defineEmits(["cancel", "save", "add-another"]);

const group = ref<Record<string, any>>({});
const manager = ref<Record<string, any>>({});
const snackbar = ref({ show: false, text: "" });

const name = computed(() => {
  return props.editMode
    ? t("groups.edit-group")
    : t("groups.create-group");
});

const formDisabled = computed(() => {
  return props.saveLoading || props.addMoreLoading;
});

watch(
  () => props.initialData,
  (groupProp) => {
    if (isEmpty(groupProp)) {
      clear();
    } else {
      group.value = groupProp;
      manager.value = parseGroup(group.value);
      group.value.manager = groupProp.managerInfo;
    }
  }
);

function getManagerName(managerInfo: any) {
  var man = managerInfo.person;
  return (
    man.firstName +
    " " +
    man.lastName +
    " " +
    (man.secondLastName ? man.secondLastName : "")
  );
}

function parseGroup(obj: any) {
  return {
    id: obj.managerId
  };
}

function updateSelection(obj: any) {
  if (obj.person) {
    group.value.managerId = obj.id;
    if (!group.value.manager) group.value.manager = {};
    group.value.manager.person = obj.person;
    if (!group.value.managerInfo) group.value.managerInfo = {};
    group.value.managerInfo.person = obj.person;
  }
}

function showSnackbar(message: string) {
  snackbar.value.text = message;
  snackbar.value.show = true;
}

function cancel() {
  clear();
  emit("cancel");
  manager.value = {};
}

function clear() {
  for (let key of Object.keys(group.value)) {
    group.value[key] = "";
  }
  delete group.value.address;
}

function validateGroup(grp: any, operation: () => void) {
  http
    .get(`/api/v1/groups/find_group/${grp.name}/${grp.manager.id}`)
    .then(response => {
      if (response.data == 0) {
        operation();
      } else {
        showSnackbar(t("groups.messages.already-exists"));
      }
    });
}

function save() {
  validateGroup(group.value, () => {
    group.value.active = true;
    emit("save", group.value);
  });
  manager.value = {};
}

function addAnother() {
  validateGroup(group.value, () => {
    group.value.active = true;
    emit("add-another", group.value);
    group.value = {};
  });
}
</script>
