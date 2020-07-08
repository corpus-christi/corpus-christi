<template>
  <v-menu>
    <v-btn id="cur-locale" data-cy="cur-locale" flat slot="activator">
      {{ currentFlagAndDescription }}
      <v-icon left>arrow_drop_down</v-icon>
    </v-btn>
    <v-list data-cy="language-dropdown">
      <v-list-tile
        v-for="(localeModel, idx) in localeModels"
        v-bind:key="idx"
        v-bind:data-cy="localeModel.code"
        v-on:click="changeLocale(localeModel)"
      >
        <v-list-tile-title>
          {{ localeModel.flagAndDescription }}
        </v-list-tile-title>
      </v-list-tile>
    </v-list>
  </v-menu>
</template>

<script lang="js">
import Vue from "vue";
import set from "lodash/set";

export default Vue.extend({
  name: "LocaleMenu",

  computed: {
    currentLocale() {
      return this.$store.state.currentLocale;
    },

    localeModels() {
      return this.$store.state.localeModels;
    },

    currentLocaleModel() {
      return this.$store.getters.currentLocaleModel;
    },

    currentFlagAndDescription() {
      const localeModel = this.currentLocaleModel;

      if (localeModel) {
        return localeModel.flagAndDescription;
      } else {
        return "NO LOCALE";
      }
    },
  },

  mounted() {
    this.getTranslationsForLanguage(this.currentLocale);
  },

  methods: {
    setCurrentLocale(locale) {
      this.$store.commit("setCurrentLocale", locale);
    },

    changeLocale(localeModel) {
      const locale = localeModel.locale;
      this.setCurrentLocale(locale);
      this.getTranslationsForLanguage(locale).then(() => {
        this.$i18n.locale = locale.toString();
      });
    },

    getTranslationsForLanguage(locale) {
      return this.$http
        .get(`/api/v1/i18n/values/${locale}`)
        .then((response) => {
          let translations = {};
          for (let item of response.data) {
            set(translations, item.key_id, item.gloss);
          }
          this.$i18n.mergeLocaleMessage(locale.languageCode, translations);
          console.log("GTFL XLATES", this.$i18n);
        })
        .catch((err) => console.error("FAILURE", err));
    },
  },
});
</script>
