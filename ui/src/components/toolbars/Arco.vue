<template>
  <v-app-bar app color="rgb(241, 145, 37)">
    <router-link v-bind:to="{ name: 'public' }" data-cy="home-logo">
      <img v-bind:src="arcoLogo" height="40px" alt="Arco Logo" />
    </router-link>

    <v-spacer />

    <v-btn
      variant="text"
      icon
      color="white"
      v-bind:to="destination"
      data-cy="account-button"
    >
      <v-icon>account_circle</v-icon>
    </v-btn>

    <LocaleMenu />
  </v-app-bar>
</template>

<script setup lang="ts">
import { computed } from "vue";
import arcoLogo from "../../../assets/arco-logo.png";
import LocaleMenu from "../LocaleMenu.vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();

const destination = computed(() => {
  if (authStore.isLoggedIn) {
    return { name: "admin" };
  } else {
    return { name: "login" };
  }
});
</script>
