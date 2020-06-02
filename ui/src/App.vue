<template>
  <v-app>
    <Toolbar />
    <v-content> <router-view /> </v-content>
    <Footer />
  </v-app>
</template>

<script>
import Toolbar from "./components/Toolbar";
import { mapMutations, mapState } from "vuex";
import Footer from "./components/Footer";
import { setJWT } from "./plugins/axios";
import { Locale } from "./models/Locale";

export default {
  name: "App",
  components: { Footer, Toolbar },
  computed: mapState(["currentJWT"]),
  methods: mapMutations(["setLocaleModels", "setCurrentLocale"]),

  created: function() {
    // Initialize early application stuff

    // Locales
    this.$http.get("/api/v1/i18n/locales").then(response => {
      const localeData = response.data;

      if (localeData && localeData.length > 0) {
        this.setLocaleModels(localeData);

        const firstLocaleString = localeData[0].code;
        this.setCurrentLocale(new Locale(firstLocaleString));
        this.$i18n.locale = firstLocaleString;
      }
    });

    // Authentication information in local storage.
    setJWT(this.currentJWT);
  }
};
</script>
