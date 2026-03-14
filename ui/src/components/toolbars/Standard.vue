<template>
  <div>
    <v-app-bar app style="z-index: 50">
      <v-app-bar-nav-icon
        v-on:click="toggleNavDrawer"
        data-cy="toggle-nav-drawer"
      ></v-app-bar-nav-icon>

      <v-toolbar-title class="headline text-uppercase">
        <span>Corpus</span> <span class="font-weight-light">Christi</span>
      </v-toolbar-title>

      <v-spacer></v-spacer>

      <AccountMenu data-cy="account-menu"></AccountMenu>
      <LocaleMenu data-cy="cur-locale"></LocaleMenu>
    </v-app-bar>

    <NavDrawer style="z-index: 100" ref="drawer"></NavDrawer>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import LocaleMenu from "../LocaleMenu.vue";
import AccountMenu from "../AccountMenu.vue";
import NavDrawer from "../NavDrawer.vue";

const drawer = ref<InstanceType<typeof NavDrawer> | null>(null);

function toggleNavDrawer() {
  drawer.value?.toggle();
}
</script>
