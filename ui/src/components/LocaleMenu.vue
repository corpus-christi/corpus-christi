<template>
  <v-menu>
    <template #activator="{ props }">
      <v-btn id="cur-locale" data-cy="cur-locale" variant="text" v-bind="props">
        {{ currentFlagAndDescription }}
        <v-icon>arrow_drop_down</v-icon>
      </v-btn>
    </template>
    <v-list data-cy="language-dropdown">
      <v-list-item
        v-for="(localeModel, idx) in authStore.localeModels"
        v-bind:key="idx"
        v-bind:data-cy="localeModel.locale.toString()"
        v-on:click="changeLocale(localeModel)"
      >
        <v-list-item-title>
          {{ localeModel.flagAndDescription }}
        </v-list-item-title>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import set from "lodash/set";
import type { AxiosInstance, AxiosResponse } from "axios";
import type { I18NValueSchema, LocaleModel } from "@/models/Locale";
import { Locale } from "@/models/Locale";
import { useAuthStore } from "@/stores/auth";

const { mergeLocaleMessage } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const authStore = useAuthStore();

const currentFlagAndDescription = computed(() => {
  const localeModel = authStore.currentLocaleModel;
  if (localeModel) {
    return localeModel.flagAndDescription;
  } else {
    return "NO LOCALE";
  }
});

onMounted(() => {
  getTranslationsForLanguage(authStore.currentLocale);
});

function setCurrentLocale(locale: Locale) {
  authStore.setCurrentLocale(locale);
}

function changeLocale(localeModel: LocaleModel) {
  const locale = localeModel.locale;
  setCurrentLocale(locale);
  getTranslationsForLanguage(locale).then(() => {
    // locale is already updated in store; i18n locale is synced via watcher or directly
  });
}

function getTranslationsForLanguage(locale: Locale): Promise<void> {
  return http
    .get(`/api/v1/i18n/values/${locale}`)
    .then((response: AxiosResponse<I18NValueSchema[]>) => {
      let translations: Record<string, unknown> = {};
      for (let item of response.data) {
        set(translations, item.key_id, item.gloss);
      }
      mergeLocaleMessage(locale.languageCode, translations);
    })
    .catch((err: unknown) => console.error("FAILURE", err));
}
</script>
