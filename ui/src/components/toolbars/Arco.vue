<template>
  <v-toolbar app color="rgb(241, 145, 37)">
    <router-link v-bind:to="{ name: 'public' }" data-cy="home-logo">
      <img v-bind:src="arcoLogo" height="40px" alt="Arco Logo" />
    </router-link>

    <v-spacer></v-spacer>

    <v-btn
      flat
      icon
      color="white"
      v-bind:to="destination"
      data-cy="account-button"
    >
      <v-icon>account_circle</v-icon>
    </v-btn>

    <LocaleMenu></LocaleMenu>
  </v-toolbar>
</template>

<script>
import arcoLogo from "../../../assets/arco-logo.png";
import LocaleMenu from "../LocaleMenu";
import { mapGetters } from "vuex";

export default {
  name: "ArcoToolbar",
  components: { LocaleMenu },
  data() {
    return {
      arcoLogo
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
    }
  }
};
</script>
