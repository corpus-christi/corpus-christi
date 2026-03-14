<template>
  <div>
    <!-- Header -->
    <v-toolbar>
      <v-row align="center" justify="space-between">
        <v-col md="2">
          <v-toolbar-title>{{ t("transcripts.transcript") }}</v-toolbar-title>
        </v-col>
        <v-spacer></v-spacer>
        <v-col md="3">
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="t('actions.search')"
            single-line
            hide-details
            data-cy="transcripts-table-search"
          ></v-text-field>
        </v-col>
      </v-row>
    </v-toolbar>

    <!-- Table of existing students -->
    <v-data-table
      :headers="headers"
      :items="showStudents"
      :loading="!tableLoaded"
      :search="search"
      class="elevation-1"
      data-cy="transcripts-table"
    >
      <template #item="{ item }">
        <tr>
          <td class="hover-hand" @click="clickThrough(item)">
            {{ item.lastName }}
          </td>
          <td class="hover-hand" @click="clickThrough(item)">
            {{ item.firstName }}
          </td>
        </tr>
      </template>
    </v-data-table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const router = useRouter();

const tableLoaded = ref(false);
const selected = ref<any[]>([]);
const students = ref<any[]>([]);
const search = ref("");
const viewStatus = ref("active");

const headers = computed(() => [
  { title: t("person.name.last"), value: "lastName", width: "40%" },
  { title: t("person.name.first"), value: "firstName", width: "60%" }
]);

const showStudents = computed(() => {
  return students.value;
});

function clickThrough(transcript: any) {
  console.log(transcript);
  router.push({
    name: "transcript-details",
    params: { studentId: transcript.id }
  });
}

onMounted(() => {
  console.log("about to fetch students....");
  http.get("/api/v1/courses/students").then(resp => {
    students.value = resp.data;
    console.log("student list received: ", students.value);
    tableLoaded.value = true;
  });
});
</script>

<style scoped>
.hover-hand {
  cursor: pointer;
}
</style>
