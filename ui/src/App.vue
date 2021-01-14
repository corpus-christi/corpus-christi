<template>
  <default-layout v-bind:bus="bus" />
</template>

<script>
import { mapMutations, mapState } from "vuex";
import { setJWT } from "./plugins/axios";
import { Locale } from "./models/Locale";
import { eventBus } from "./plugins/event-bus.js";
import DefaultLayout from "./layouts/DefaultLayout";

export default {
  name: "App",
  components: {
    DefaultLayout,
  },
  computed: mapState(["currentJWT"]),
  methods: mapMutations(["setLocaleModels", "setCurrentLocale"]),

  created: function () {
    // Initialize early application stuff

    // Locales
    this.$http.get("/api/v1/i18n/locales")
    .then((response) => {
      const localeData = response.data;

      if (localeData && localeData.length > 0) {
        this.setLocaleModels(localeData);

        let langs=navigator.languages;

        let needLang=true;

        langs.forEach((lang)=>{
            localeData.forEach((loc)=>{
                if(needLang && lang==loc.code){
                    this.setCurrentLocale(new Locale(lang));
                    this.$i18n.locale = lang;
                    needLang=false;
                }
            })
        })


        // If the double forEach fails, that means that none
        // of the user's languages are a current locale.
        // Default to English-US.
        if(needLang){
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
