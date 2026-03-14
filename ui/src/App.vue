<template>
  <v-app>
    <Toolbar />
    <v-main><router-view /></v-main>
    <Footer />
  </v-app>
</template>

<script setup lang="ts">
import { inject, onBeforeMount } from "vue";
import type { AxiosInstance } from "axios";
import Toolbar from "./components/Toolbar.vue";
import Footer from "./components/Footer.vue";
import { setJWT } from "./plugins/axios";
import { Locale } from "./models/Locale";
import { useAuthStore } from "./stores/auth";
import { useI18n } from "vue-i18n";

const authStore = useAuthStore();
const { locale } = useI18n();
const http = inject<AxiosInstance>("$http")!;

onBeforeMount(() => {
  // Initialize JWT from stored value
  setJWT(authStore.currentJWT);

  // Load locale models from API
  http.get("/api/v1/i18n/locales").then(response => {
    const localeData = response.data;
    if (localeData && localeData.length > 0) {
      authStore.setLocaleModels(localeData);
      const firstLocaleString = localeData[0].code;
      authStore.setCurrentLocale(new Locale(firstLocaleString));
      locale.value = firstLocaleString;
    }
  });
});
</script>
