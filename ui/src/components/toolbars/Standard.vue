<template>
  <div>
    <v-toolbar app>
      <v-toolbar-side-icon v-on:click="toggleNavDrawer"></v-toolbar-side-icon>

      <v-toolbar-title class="headline text-uppercase">
        <span>Corpus</span> <span class="font-weight-light">Christi</span>
      </v-toolbar-title>

      <v-spacer></v-spacer>

      <LocaleMenu></LocaleMenu>
    </v-toolbar>

    <v-navigation-drawer app v-model="showNavDrawer">
      <v-list>
        <v-list-tile v-bind:to="{ name: 'home' }">
          <v-list-tile-action> <v-icon>home</v-icon> </v-list-tile-action>
          <v-list-tile-title>Home</v-list-tile-title>
        </v-list-tile>
        <v-list-tile v-bind:to="{ name: 'people' }">People</v-list-tile>
      </v-list>
    </v-navigation-drawer>
  </div>
</template>

<script>
import LocaleMenu from "../LocaleMenu";
export default {
  name: "StandardToolbar",
  components: { LocaleMenu },
  data() {
    return {
      showNavDrawer: false
    };
  },
  methods: {
    toggleNavDrawer() {
      this.showNavDrawer = !this.showNavDrawer;
    }
  }
};
</script>
