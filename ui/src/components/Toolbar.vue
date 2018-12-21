<template>
  <v-toolbar app>
    <v-toolbar-title class="headline text-uppercase">
      <span>Corpus</span> <span class="font-weight-light">Christi</span>
    </v-toolbar-title>
    <v-spacer></v-spacer>

    <v-menu>
      <v-btn id="cur-locale" flat slot="activator">
        {{ displayLocale(currentLocale) }}
      </v-btn>
      <v-list>
        <v-list-tile
          v-for="locale in locales"
          v-bind:key="locale.code"
          v-on:click="setCurrentLocale(locale)"
        >
          <v-list-tile-title>{{ displayLocale(locale) }}</v-list-tile-title>
        </v-list-tile>
      </v-list>
    </v-menu>

    <v-btn flat v-bind:to="{ name: 'home' }">Home</v-btn>
  </v-toolbar>
</template>

<script>
import { mapGetters, mapMutations, mapState } from "vuex";
import { flagForLocale, splitLocaleCode } from "../helpers";

export default {
  name: "Toolbar",
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
