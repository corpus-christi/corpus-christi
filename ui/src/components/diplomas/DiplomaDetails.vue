<template>
  <v-row wrap>
    <v-col cols="12">
      <v-btn
        variant="outlined"
        color="primary"
        v-on:click="router.push({ name: 'all-diplomas' })"
        ><v-icon>arrow_back</v-icon>{{ t("actions.back") }}</v-btn
      >
    </v-col>
    <v-col cols="12" sm="8" offset-sm="2">
      <v-card>
        <template v-if="loading">
          <v-container fill-height fluid>
            <v-row align="center" justify="center">
              <v-progress-circular color="primary" indeterminate />
            </v-row>
          </v-container>
        </template>
        <template v-else>
          <v-row>
            <v-col cols="12">
              <v-card>
                <v-toolbar color="primary">
                  <v-toolbar-title>
                    {{ t("diplomas.diploma") }}: {{ diploma.name }}
                  </v-toolbar-title>
                </v-toolbar>
                <v-list lines="three">
                  <v-list-subheader> {{ diploma.description }} </v-list-subheader>
                  <v-list-subheader
                    >{{ t("diplomas.courses-this-diploma") }}:</v-list-subheader
                  >
                  <template v-for="(course, index) in diploma.courseList" :key="index">
                    <v-list-item>
                      <v-list-item-title v-html="course.name"></v-list-item-title>
                      <v-list-item-subtitle v-html="course.description"></v-list-item-subtitle>
                    </v-list-item>
                  </template>
                </v-list>
              </v-card>
            </v-col>
          </v-row>
        </template>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter, useRoute } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const router = useRouter();
const route = useRoute();

const props = defineProps<{
  diplomaId: string | number;
}>();

const diploma = ref<Record<string, any>>({});
const loading = ref(true);
const loadingFailed = ref(false);

watch(route, () => {
  loadDiploma();
});

onMounted(() => {
  loadDiploma();
});

function loadDiploma() {
  loading.value = true;
  loadingFailed.value = false;
  http
    .get(`/api/v1/courses/diplomas/${props.diplomaId}`)
    .then(resp => {
      diploma.value = resp.data;
    })
    .catch(() => {
      loadingFailed.value = true;
    })
    .finally(() => {
      loading.value = false;
    });
}
</script>

<style></style>
