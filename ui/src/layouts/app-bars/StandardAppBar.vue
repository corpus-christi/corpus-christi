<template>
  <v-app-bar app clipped-left>
    <v-app-bar-nav-icon
      v-on:click="toggleNavDrawer"
      data-cy="toggle-nav-drawer"
    ></v-app-bar-nav-icon>

    <v-toolbar-title class="headline text-uppercase">
      <span>Corpus</span>
      <span class="font-weight-light">Christi</span>
    </v-toolbar-title>

    <v-spacer />

    <account-menu data-cy="account-menu" />
    <locale-menu data-cy="cur-locale" />
  </v-app-bar>
</template>

<script>
import LocaleMenu from "../menus/LocaleMenu";
import AccountMenu from "../menus/AccountMenu";

export default {
  name: "StandardAppBar",
  components: { AccountMenu, LocaleMenu },
  methods: {
    // Holding a reference to the navigation drawer is not good separation of concerns,
    // but it greatly simplifies this interaction.
    toggleNavDrawer() {
      this.$refs.drawer.toggle();
    },
  },
};
</script>
