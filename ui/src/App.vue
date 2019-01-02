<template>
  <v-app>
    <Toolbar></Toolbar>
    <v-content> <router-view></router-view> </v-content>
    <Footer></Footer>
  </v-app>
</template>

<script>
import Toolbar from "./components/Toolbar";
import { mapGetters, mapMutations } from "vuex";
import { splitLocaleCode } from "./helpers";
import Footer from "./components/Footer";
import { setJWT } from "./plugins/axios";

export default {
  name: "App",
  components: { Footer, Toolbar },
  computed: mapGetters(["currentJWT"]),
  methods: mapMutations(["setLocales", "setCurrentLocaleCode"]),
  created: function() {
    // Initialize early application stuff

    // Locales
    this.$http.get("/api/v1/i18n/locales").then(response => {
      const locales = response.data;
      this.setLocales(locales);

      const firstLocale = locales[0];
      this.setCurrentLocaleCode(firstLocale.code);
      this.$i18n.locale = splitLocaleCode(firstLocale.code).languageCode;
    });

    // Authentication information in local storage.
    setJWT(this.currentJWT);
  }
};
</script>
