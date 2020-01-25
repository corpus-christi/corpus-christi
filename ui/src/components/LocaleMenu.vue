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

<script lang="ts">
import Vue from "vue";
import set from "lodash/set";
import { I18NValueSchema, Locale, LocaleModel } from "@/models/Locale";
import { AxiosResponse, AxiosError } from "axios";

export default Vue.extend({
  name: "LocaleMenu",

  computed: {
    currentLocale(): Locale {
      return this.$store.state.currentLocale;
    },

    localeModels(): LocaleModel[] {
      return this.$store.state.localeModels;
    },

    currentLocaleModel(): LocaleModel {
      return this.$store.getters.currentLocaleModel;
    },

    currentFlagAndDescription(): string {
      const localeModel = this.currentLocaleModel;

      if (localeModel) {
        return localeModel.flagAndDescription;
      } else {
        return "NO LOCALE";
      }
    }
  },

  mounted() {
    this.getTranslationsForLanguage(this.currentLocale);
  },

  methods: {
    setCurrentLocale(locale: Locale) {
      this.$store.commit("setCurrentLocale", locale);
    },

    changeLocale(localeModel: LocaleModel) {
      console.log("CH LOC", localeModel);
      const locale = localeModel.locale;
      this.setCurrentLocale(locale);
      this.getTranslationsForLanguage(locale).then(() => {
        this.$i18n.locale = locale.toString();
      });
    },

    getTranslationsForLanguage(locale: Locale): Promise<void> {
      console.log("GTFL", locale);
      return this.$http
        .get(`/api/v1/i18n/values/${locale}`)
        .then((response: AxiosResponse<I18NValueSchema[]>) => {
          let translations = {};
          for (let item of response.data) {
            set(translations, item.key_id, item.gloss);
          }
          console.log("THIS.I18N", this.$i18n);
          this.$i18n.mergeLocaleMessage(locale.languageCode, translations);
          console.log("GTFL XLATES", this.$i18n);
        })
        .catch((err: AxiosError) => console.error("FAILURE", err));
    }
  }
});
</script>
