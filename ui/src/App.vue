<template>
  <v-app>
    <Toolbar></Toolbar>
    <v-content>
      <v-container> <router-view></router-view> </v-container>
    </v-content>
  </v-app>
</template>

<script>
import Toolbar from "./components/Toolbar";
import { mapMutations } from "vuex";
import { splitLocaleCode } from "./helpers";
import axios from "axios";

export default {
  name: "App",
  components: { Toolbar },
  methods: mapMutations(["setLocales", "setCurrentLocaleCode"]),
  created: function() {
    // Initialize early application stuff
    axios.get("/api/v1/i18n/locales").then(response => {
      const locales = response.data;
      this.setLocales(locales);

      const firstLocale = locales[0];
      this.setCurrentLocaleCode(firstLocale.code);
      this.$i18n.locale = splitLocaleCode(firstLocale.code).languageCode;
    });
  }
};
</script>
