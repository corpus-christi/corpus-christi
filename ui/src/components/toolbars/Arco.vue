<template>
  <v-toolbar app color="rgb(241, 145, 37)">
    <img v-bind:src="arcoLogo" height="40px" alt="Arco Logo" />

    <v-spacer></v-spacer>

    <v-btn flat icon color="white" v-bind:to="{ name: 'login' }">
      <v-icon>account_circle</v-icon>
    </v-btn>

    <LocaleMenu></LocaleMenu>
  </v-toolbar>
</template>

<script>
import arcoLogo from "../../../assets/arco-logo.png";
import LocaleMenu from "../LocaleMenu";

export default {
  name: "ArcoToolbar",
  components: { LocaleMenu },
  data() {
    return {
      arcoLogo
    };
  }
};
</script>
