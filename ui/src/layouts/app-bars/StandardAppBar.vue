<template>
  <div>
    <!-- The hamburger button that displays the NavDrawer menu -->
    <v-app-bar app clipped-left>
      <v-app-bar-nav-icon
        v-on:click="toggleNavDrawer"
        data-cy="toggle-nav-drawer"
      />

      <!-- Write CorpusChristi on the App Bar -->
      <v-toolbar-title class="headline text-uppercase">
        <span>Corpus</span>
        <span class="font-weight-light">Christi</span>
      </v-toolbar-title>
      <v-spacer />

      <!-- Draw the Account Menu -->
      <account-menu data-cy="account-menu" />
      <!-- Draw the Locale Menu -->
      <locale-menu data-cy="cur-locale" />
    </v-app-bar>

    <!-- Draw the NavDrawer -->
    <nav-drawer v-model="navDrawerVisible" />
  </div>
</template>

<script>
/**
 * @file
 * @name StandardAppBar.vue
 */
import LocaleMenu from "../menus/LocaleMenu";
import AccountMenu from "../menus/AccountMenu";
import NavDrawer from "../NavDrawer";

/**
 * @file
 * @name StandardAppBar
 * @exports ../AppBar.vue
 * Actually Draws the App Bar.
 */
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
