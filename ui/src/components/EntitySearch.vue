<template>
  <div>
    <v-autocomplete
      data-cy="entity-search-field"
      v-bind:label="getLabel"
      prepend-icon="search"
      :items="searchableEntities"
      :loading="isLoading"
      :model-value="value"
      v-on:update:model-value="setSelected"
      v-model:search="searchInput"
      v-bind:error-messages="errorMessages"
      return-object
      :custom-filter="customFilter"
      :multiple="multiple"
      menu-props="closeOnClick, closeOnContentClick"
      :value-comparator="compare"
      color="secondary"
      :disabled="disabled"
    >
      <template v-if="!multiple" #selection="data">
        {{ getEntityDescription(data.item.raw, 100) }}
      </template>
      <template #item="data">
        <v-list-item v-bind="data.props">
          <template #prepend>
            <span v-if="multiple && selectionContains(data.item.raw)">
              <v-icon>clear</v-icon>
            </span>
          </template>
          <v-list-item-title>{{ getEntityDescription(data.item.raw) }}</v-list-item-title>
        </v-list-item>
      </template>
    </v-autocomplete>
    <template v-if="multiple">
      <div v-for="entity in value" v-bind:key="entity[idField]">
        <v-chip
          closable
          @click:close="remove(entity)"
          :data-cy="'chip-' + entity[idField]"
        >
          {{ getEntityDescription(entity) }}
        </v-chip>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;

const props = defineProps<{
  location?: boolean;
  person?: boolean;
  course?: boolean;
  team?: boolean;
  address?: boolean;
  manager?: boolean;
  asset?: boolean;
  group?: boolean;
  meeting?: boolean;
  multiple?: boolean;
  existingEntities?: any[];
  value?: any;
  searchEndpoint?: string;
  errorMessages?: string;
  label?: string;
  disabled?: boolean;
}>();

const emit = defineEmits(["input"]);

const descriptionLimit = 50;
const entities = ref<any[]>([]);
const searchInput = ref("");
const isLoading = ref(false);

const idField = "id";

watch(() => props.value, (val) => {
  setSelected(val);
});

const getLabel = computed(() => {
  if (props.label) return props.label;
  else if (props.location) return t("events.event-location");
  else if (props.person) return t("actions.search-people");
  else if (props.course) return t("actions.search-courses");
  else if (props.team) return t("teams.title");
  else if (props.address) return t("actions.search-addresses");
  else if (props.manager) return t("actions.search-managers");
  else if (props.asset) return t("assets.title");
  else if (props.group) return t("groups.title");
  else if (props.meeting) return t("groups.meetings.title");
  else return "";
});

const searchableEntities = computed(() => {
  if (props.existingEntities) {
    return entities.value.filter(ent => {
      for (let otherEnt of props.existingEntities!) {
        if (ent[idField] === otherEnt[idField]) {
          return false;
        }
      }
      return true;
    });
  }
  return entities.value;
});

function selectionContains(entity: any) {
  if (!props.value || !props.value.length) return false;
  var idx = props.value.findIndex((en: any) => en[idField] === entity[idField]);
  return idx > -1;
}

function setSelected(entity: any) {
  emit("input", entity);
}

function getEntityDescription(entity: any, letterLimit = descriptionLimit): string {
  if (!entity) return "";
  let entityDescriptor = "";
  if (props.location) {
    entityDescriptor =
      entity.description +
      ", " +
      entity.address.address +
      ", " +
      entity.address.city;
  } else if (props.person) {
    entityDescriptor = entity.firstName + " " + entity.lastName;
  } else if (props.course) {
    entityDescriptor = entity.name;
  } else if (props.team) {
    entityDescriptor = entity.description;
  } else if (props.address) {
    entityDescriptor = entity.name + ", " + entity.address;
  } else if (props.manager) {
    var person = entity.person;
    entityDescriptor =
      person.firstName +
      " " +
      person.lastName +
      " " +
      (person.secondLastName ? person.secondLastName : "");
  } else if (props.asset) {
    entityDescriptor = entity.description;
  } else if (props.group) {
    entityDescriptor = entity.description;
  } else if (props.meeting) {
    entityDescriptor = entity.description;
  }
  if (entityDescriptor.length > letterLimit) {
    entityDescriptor = entityDescriptor.substring(0, letterLimit) + "...";
  }
  return entityDescriptor;
}

function customFilter(item: any, queryText: string) {
  const itemDesc = getEntityDescription(item).toLowerCase();
  const searchText = queryText.toLowerCase();
  return itemDesc.indexOf(searchText) > -1;
}

function remove(entity: any) {
  if (!props.multiple) return;
  var idx = props.value.findIndex((en: any) => en[idField] === entity[idField]);
  if (idx > -1) {
    props.value.splice(idx, 1);
  }
}

function compare(a: any, b: any) {
  if (!a || !b) return false;
  return a[idField] === b[idField];
}

onMounted(() => {
  isLoading.value = true;
  var endpoint = "";
  if (props.location) endpoint = "/api/v1/places/locations";
  else if (props.person) endpoint = "/api/v1/people/persons";
  else if (props.course) endpoint = "/api/v1/courses/courses";
  else if (props.team) endpoint = "/api/v1/teams/";
  else if (props.asset) endpoint = "/api/v1/assets/";
  else if (props.address) endpoint = "/api/v1/places/addresses";
  else if (props.manager)
    endpoint = "/api/v1/people/manager?show_unique_persons_only=Y";
  else if (props.group) endpoint = "/api/v1/groups/groups";
  else if (props.meeting) endpoint = "/api/v1/groups/meetings";
  http
    .get(endpoint)
    .then(resp => {
      entities.value = resp.data;
      isLoading.value = false;
    })
    .catch(error => {
      console.log(error);
      isLoading.value = false;
    });
});
</script>
