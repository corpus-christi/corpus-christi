<template>
  <div>
    <v-menu offset-y v-if="authStore.isLoggedIn">
      <template #activator="{ props }">
        <v-btn id="cur-locale" variant="text" v-bind="props">
          {{ authStore.currentAccount.fullName() }}
          <v-icon>arrow_drop_down</v-icon>
        </v-btn>
      </template>

      <v-list>
        <v-list-item v-on:click="logAccountOut" data-cy="logout">
          <v-list-item-title> {{ t("actions.logout") }} </v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>

    <v-btn v-else variant="text" icon v-bind:to="{ name: 'login' }" data-cy="login">
      <v-icon>account_circle</v-icon>
    </v-btn>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
const authStore = useAuthStore();
const router = useRouter();

function logAccountOut() {
  authStore.logOut();
  router.push({ name: "public" });
}
</script>
