<template>
  <v-menu>
    <v-btn id="cur-locale" data-cy="cur-locale" flat slot="activator">
      {{ displayLocale(currentLocale) }}
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
export default {
  name: "LocaleMenu",

  computed: {
    ...mapState(["locales"]),
    ...mapGetters(["currentLocale"])
  },

  methods: {
    ...mapMutations(["setCurrentLocaleCode"]),

    setCurrentLocale(locale) {
      // Set the current locale.
      this.setCurrentLocaleCode(locale.code);
      this.$i18n.locale = splitLocaleCode(locale.code).languageCode;
    },

    displayLocale(locale) {
      // Return a string that displays the current locale and its flag.
      if (!locale) {
        return "";
      }
      return flagForLocale(locale.code) + locale.desc;
    }
  }
};
</script>

<style scoped></style>
