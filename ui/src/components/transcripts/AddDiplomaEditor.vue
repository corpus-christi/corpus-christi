<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ name }}</span>
    </v-card-title>
    <v-card-text>
      <v-form>
        <v-select
          v-model="diploma.id"
          :items="items"
          v-bind:label="t('diplomas.diploma')"
          variant="outlined"
          item-value="id"
          item-title="name"
          :menu-props="{ closeOnContentClick: true }"
          required
        ></v-select>
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-btn color="secondary" variant="text" :disabled="saving" v-on:click="cancel">{{
        t("actions.cancel")
      }}</v-btn>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        variant="elevated"
        :disabled="saving || !diploma.id"
        :loading="saving"
        v-on:click="save"
        >{{ t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;

const props = defineProps<{
  diplomasThisStudent: any[];
  saving?: boolean;
}>();

const emit = defineEmits(["cancel", "save"]);

const diploma = ref<any>({});
const diplomasPool = ref<any[]>([]);

const name = computed(() => t("diplomas.new"));

const items = computed(() => {
  return diplomasPool.value.filter(
    d => !props.diplomasThisStudent.includes(d.id)
  );
});

function cancel() {
  diploma.value = {};
  emit("cancel");
}

function save() {
  if (diploma.value.id) {
    emit("save", diploma.value);
  }
}

onMounted(() => {
  http.get("/api/v1/courses/diplomas").then(resp => {
    diplomasPool.value = [];
    resp.data.forEach((d: any) => {
      diplomasPool.value.push({
        name: d.name,
        id: d.id
      });
    });
  });
});
</script>
