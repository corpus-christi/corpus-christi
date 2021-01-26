<template>
  <!-- COLOR! -->
  <v-app-bar app color="rgb(241, 145, 37)">
    <!-- Draw the Arco logo. Make it link to this page for some reason. -->
    <router-link v-bind:to="{ name: 'public' }" data-cy="home-logo">
      <img v-bind:src="arcoLogo" height="40px" alt="Arco Logo" />
    </router-link>

    <v-spacer />

    <!-- Draw a Login button on the App Bar. -->
    <v-btn
      text
      icon
      color="white"
      v-bind:to="destination"
      data-cy="account-button"
    >
      <v-icon>account_circle</v-icon>
    </v-btn>

    <!-- Draw the Locale Menu. -->
    <locale-menu />
  </v-app-bar>
</template>

<script>
/**
 * @file
 * @name ArcoAppBar.vue
 */
import arcoLogo from "../../../assets/arco-logo.png";
import LocaleMenu from "../menus/LocaleMenu";
import { mapGetters } from "vuex";

/**
 * @module
 * @name AcroAppBar
 * @exports ../AppBar.vue
 * Draw the App Bar for the Arco Public Home Page.
 */
export default {
  name: "ArcoAppBar",
  components: { LocaleMenu },

  data() {
    return {
      arcoLogo,
    };
  },

  computed: {
    ...mapGetters(["isLoggedIn"]),
    destination() {
      if (this.isLoggedIn) {
        return { name: "admin" };
      } else {
        return { name: "login" };
      }
    },
  },
};
</script>
