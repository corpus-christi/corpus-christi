<template>
  <v-menu>
    <v-btn id="cur-locale" flat slot="activator" data-cy="">
      {{ displayLocale(currentLocale) }}
    </v-btn>
    <v-list>
      <v-list-tile
        v-for="locale in locales"
        v-bind:key="locale.code"
        v-on:click="setCurrentLocale(locale)"
        data-cy=""
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
