<template>
  <div>
    <v-app-bar app clipped-left>
      <v-app-bar-nav-icon
        v-on:click="toggleNavDrawer"
        data-cy="toggle-nav-drawer"
      />

      <v-toolbar-title class="headline text-uppercase">
        <span>Corpus</span>
        <span class="font-weight-light">Christi</span>
      </v-toolbar-title>

      <v-spacer />

      <account-menu data-cy="account-menu" />
      <locale-menu data-cy="cur-locale" />
    </v-app-bar>

    <nav-drawer v-model="navDrawerVisible" />
  </div>
</template>

<script>
import LocaleMenu from "../menus/LocaleMenu";
import AccountMenu from "../menus/AccountMenu";
import NavDrawer from "../NavDrawer";

export default {
  name: "StandardAppBar",
  components: { NavDrawer, AccountMenu, LocaleMenu },

  data() {
    return {
      navDrawerVisible: false,
    };
  },

  methods: {
    toggleNavDrawer() {
      this.navDrawerVisible = !this.navDrawerVisible;
    },
  },
};
</script>
