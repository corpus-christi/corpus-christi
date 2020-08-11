<template>
  <v-menu offset-y :disabled="ableMenu">
    <template v-slot:activator="{ on }">
      <v-btn id="cur-locale" data-cy="cur-locale" text v-on="on">
        {{ currentFlagAndDescription }}
        <v-icon>arrow_drop_down</v-icon>
      </v-btn>
    </template>

    <v-list data-cy="language-dropdown">
      <v-list-item
        v-for="(localeModel, idx) in localeModels"
        v-bind:key="idx"
        v-bind:data-cy="localeModel.code"
        v-on:click="changeLocale(localeModel)"
      >
        <v-list-item-title>
          {{ localeModel.flagAndDescription }}
        </v-list-item-title>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script lang="js">
import Vue from "vue";
import set from "lodash/set";
import { mapState } from "vuex";

export default Vue.extend({
  name: "LocaleMenu",

  computed: {
    ...mapState(["currentAccount"]),

    ableMenu(){
      if (this.currentAccount == null){
        return false
      }
      else{
        if (this.currentAccount.roles.includes("role.translator") && this.$route.name === "translation"){
          return true
        }
        else return false;
      }
    },

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
