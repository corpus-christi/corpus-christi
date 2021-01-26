<template>
  <default-layout v-bind:bus="bus" />
</template>

<script>
import { mapMutations, mapState } from "vuex";
import { setJWT } from "./plugins/axios";
import { Locale } from "./models/Locale";
import { eventBus } from "./plugins/event-bus.js";
import DefaultLayout from "./layouts/DefaultLayout";
import { mapGetters } from 'vuex';

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

  created: function () {
    // Initialize early application stuff

    // Locales
    this.$http.get("/api/v1/i18n/locales").then((response) => {
      const localeData = response.data;

      
      if (localeData && localeData.length > 0) {
        this.setLocaleModels(localeData);
        let firstLocaleString;
                                                        
        if (this.currentLocaleModel.languageCode) {     //Check if Vuex has a Language Setting stored already
          firstLocaleString = this.currentLocaleModel.languageCode + '-' + this.currentLocaleModel.countryCode;
        } else {
          firstLocaleString = navigator.language;       //Otherwise, pull the Browser's Default Language, and check if it's in the database
          let validLanguageBool = false;
          for(let i = 0; i < localeData.length; i++) {
            if (localeData[i].code == firstLocaleString) {
              validLanguageBool = true;
              break;
            }
          }
          if (!validLanguageBool) {                     //If all else fails, default to US English.
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
