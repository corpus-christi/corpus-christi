<template>
  <default-layout v-bind:bus="bus" />
</template>

<script>
/**
 * @file
 * @name App.vue
 * @exports main.ts
 * Main App. Does Initialization.
 */
import { mapMutations, mapState } from "vuex";
import { setJWT } from "./plugins/axios";
import { Locale } from "./models/Locale";
import { eventBus } from "./plugins/event-bus.js";
import DefaultLayout from "./layouts/DefaultLayout";
import { mapGetters } from "vuex";

export default {
  name: "App",
  components: {
    DefaultLayout,
  },
  computed: {
    ...mapState(["currentJWT"]),
    ...mapGetters(["currentLocaleModel"]),
  },
  methods: mapMutations(["setLocaleModels", "setCurrentLocale"]),

  /**
   * @function
   * Initialize early application stuff
   */
  created: function () {
    // Locales
    this.$http.get("/api/v1/i18n/locales").then((response) => {
      const localeData = response.data;

      if (localeData && localeData.length > 0) {
        this.setLocaleModels(localeData);

        let langData = navigator.languages;
        let needLang = true;

        // find an exact match for the locale
        langData.forEach((lang) => {
          localeData.forEach((loc) => {
            if (needLang && lang == loc.code) {
              this.setCurrentLocale(new Locale(lang));
              this.$i18n.locale = lang;
              needLang = false;
            }
          });
        });
        // find an approximate match for the locale
        langData.forEach((lang) => {
          localeData.forEach((loc) => {
            if (needLang && loc.code.includes(lang.substr(0, 2))) {
              this.setCurrentLocale(new Locale(lang));
              this.$i18n.locale = lang;
              needLang = false;
            }
          });
        });

        // None of the user's languages is available. Default to en-US
        if (needLang) {
          this.setCurrentLocale(new Locale("en-US"));
          this.$i18n.locale = "en-US";
        }
      }
    });

    // Authentication information in local storage.
    setJWT(this.currentJWT);
  },

  data() {
    return {
      bus: eventBus,
    };
  },
};
</script>
