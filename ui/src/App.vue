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
        let firstLocaleString;
        //Check if Vuex has a Language Setting stored already
        if (this.currentLocaleModel.languageCode) {
          firstLocaleString =
            this.currentLocaleModel.languageCode +
            "-" +
            this.currentLocaleModel.countryCode;
        }
        //Otherwise, pull the Browser's Default Language, and check if it's in the database
        else {
          firstLocaleString = navigator.language;
          let validLanguageBool = false;
          for (let i = 0; i < localeData.length; i++) {
            if (localeData[i].code == firstLocaleString) {
              validLanguageBool = true;
              break;
            }
          }
          //If all else fails, default to US English.
          if (!validLanguageBool) {
            firstLocaleString = localeData[1].code;
          }
        }
        this.setCurrentLocale(new Locale(firstLocaleString));
        this.$i18n.locale = firstLocaleString;
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
