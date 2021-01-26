<template>
  <default-layout v-bind:bus="bus" />
</template>

<script>
/**
 * @file
 * @name App.vue
 * Main App. Does Initialization.
 * Runs from 'main.ts'
 */
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

        const firstLocaleString = localeData[0].code;
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
