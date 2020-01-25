<template>
  <v-app>
    <Toolbar />
    <v-content> <router-view /> </v-content>
    <Footer />
  </v-app>
</template>

<script>
import Toolbar from "./components/Toolbar";
import { mapGetters, mapMutations } from "vuex";
import Footer from "./components/Footer";
import { setJWT } from "./plugins/axios";

export default {
  name: "App",
  components: { Footer, Toolbar },
  computed: mapGetters(["currentJWT"]),
  methods: mapMutations(["setLocaleModels", "setCurrentLocale"]),

  created: function() {
    // Initialize early application stuff

    // Locales
    this.$http.get("/api/v1/i18n/locales").then(response => {
      console.log("APP.VUE RESPONSE", response);
      const localeData = response.data;

      if (localeData && localeData.length) {
        this.setLocaleModels(localeData);

        const firstLocaleDatum = localeData[0];
        this.setCurrentLocale(firstLocaleDatum);
        this.$i18n.locale = firstLocaleDatum.locale
        console.log("I18N LOCALE", this.$i18n);
      }
    });

    // Authentication information in local storage.
    setJWT(this.currentJWT);
  }
};
</script>
