<template>
  <v-row class="shrink" align="center">
    <v-col v-if="isTranslator" cols="5">
      <v-switch
        hide-details
        :label="$t('translation.transparent-mode')"
        @change="switchTransparentMode"
        v-model="transparentMode"
      />
    </v-col>
    <v-col>
      <v-menu offset-y>
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
              {{ getFlagAndDescription(localeModel) }}
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-col>
  </v-row>
</template>

<script>
import set from "lodash/set";
import { mapState } from "vuex";

export default {
  name: "LocaleMenu",
  data() {
    return {
      transparentMode: false,
      defaultFallbackLocale: null,
    };
  },
  computed: {
    ...mapState(["currentAccount"]),

    isTranslator() {
      return (
        this.currentAccount &&
        this.currentAccount.roles.includes("role.translator")
      );
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
        return this.getFlagAndDescription(localeModel);
      } else {
        return "NO LOCALE";
      }
    },
  },

  mounted() {
    this.getTranslationsForLanguage(this.currentLocale);
  },

  methods: {
    switchTransparentMode(enable) {
      if (enable) {
        this.defaultFallbackLocale = this.$i18n.fallbackLocale;
        this.$i18n.fallbackLocale = null; // disable fallback
        this.$i18n.locale = "transparent"; // set non-existent locale
      } else {
        this.$i18n.fallbackLocale = this.defaultFallbackLocale; // enable fallback
        this.$i18n.locale = this.currentLocale.toString(); // switch back to actual locale
      }
      console.log("this.$i18n.fallbackLocale", this.$i18n.fallbackLocale);
    },

    getFlagAndDescription(localeModel) {
      return localeModel.flagAndDescription; // plain description in database
    },

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
          this.$i18n.mergeLocaleMessage(locale.toString(), translations);
          console.log("GTFL XLATES", this.$i18n);
        })
        .catch((err) => console.error("FAILURE", err));
    },
  },
};
</script>
