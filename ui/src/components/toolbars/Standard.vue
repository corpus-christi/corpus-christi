<template>
  <div>
    <v-toolbar app>
      <v-toolbar-side-icon
        v-on:click="toggleNavDrawer"
        data-cy=""
      ></v-toolbar-side-icon>

      <v-toolbar-title class="headline text-uppercase">
        <span>Corpus</span> <span class="font-weight-light">Christi</span>
      </v-toolbar-title>

      <v-spacer></v-spacer>

      <AccountMenu></AccountMenu>
      <LocaleMenu></LocaleMenu>
    </v-toolbar>

    <NavDrawer ref="drawer"></NavDrawer>
  </div>
</template>

<script>
import LocaleMenu from "../LocaleMenu";
import AccountMenu from "../AccountMenu";
import NavDrawer from "../NavDrawer";

export default {
  name: "StandardToolbar",
  components: { NavDrawer, AccountMenu, LocaleMenu },
  methods: {
    // Holding a reference to the navigation drawer is not good separation of concerns,
    // but it greatly simplifies this interaction.
    toggleNavDrawer() {
      this.$refs.drawer.toggle();
    }
  }
};
</script>
