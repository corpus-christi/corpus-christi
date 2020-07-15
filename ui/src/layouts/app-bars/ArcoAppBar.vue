<template>
  <v-app-bar app color="rgb(241, 145, 37)">
    <router-link v-bind:to="{ name: 'public' }" data-cy="home-logo">
      <img v-bind:src="arcoLogo" height="40px" alt="Arco Logo" />
    </router-link>

    <v-spacer />

    <v-btn
      text
      icon
      color="white"
      v-bind:to="destination"
      data-cy="account-button"
    >
      <v-icon>account_circle</v-icon>
    </v-btn>

    <locale-menu />
  </v-app-bar>
</template>

<script>
import arcoLogo from "../../../assets/arco-logo.png";
import LocaleMenu from "../menus/LocaleMenu";
import { mapGetters } from "vuex";

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
