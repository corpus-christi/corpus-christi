<template>
  <v-menu>
    <v-btn id="cur-locale" data-cy="cur-locale" flat slot="activator">
      {{ displayLocale(currentLocale) }}
      <v-icon left>arrow_drop_down</v-icon>
    </v-btn>
    <v-list data-cy="language-dropdown">
      <v-list-tile
        v-for="locale in locales"
        v-bind:key="locale.code"
        v-on:click="setCurrentLocale(locale)"
        v-bind:id="locale.code"
        v-bind:data-cy="locale.code"
      >
        <v-list-tile-title>{{ displayLocale(locale) }}</v-list-tile-title>
      </v-list-tile>
    </v-list>
  </v-menu>
</template>

<script>
import { mapGetters, mapMutations, mapState } from "vuex";
import { flagForLocale, splitLocaleCode } from "../helpers";
import dotProp from "dot-prop";
import store from "./../store";

export default {
  name: "LocaleMenu",

  computed: {
    ...mapState(["locales"]),
    ...mapGetters(["currentLocale"])
  },

  mounted() {
    this.getTranslationsForLocale();
  },

  methods: {
    ...mapMutations(["setCurrentLocaleCode"]),

    setCurrentLocale(locale) {
      // Set the current locale.
      this.setCurrentLocaleCode(locale.code);
      this.$i18n.locale = splitLocaleCode(locale.code).languageCode;
      this.getTranslationsForLocale();
    },

    displayLocale(locale) {
      // Return a string that displays the current locale and its flag.
      if (!locale) {
        return "";
      }
      return flagForLocale(locale.code) + locale.desc;
    },

    getTranslationsForLocale() {
      this.translations = {};
      return this.$http
        .get(`/api/v1/i18n/values/${store.state.currentLocaleCode}`)
        .then(response => {
          let translations = {};
          for (let item of response.data) {
            dotProp.set(translations, item.key_id, item.gloss);
          }
          this.$i18n.mergeLocaleMessage(this.$i18n.locale, translations);
        })
        .catch(err => console.error("FAILURE", err.response));
    }
  }
};
</script>

<style scoped></style>
