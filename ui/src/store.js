/**
 * @file
 * @name store.js
 * Vuex Store. Contains global state information for the entire UI.
 * Runs from 'main.ts'
 */

import Vue from "vue";
import Vuex from "vuex";
import { setJWT } from "./plugins/axios";
import { Locale, LocaleModel } from "./models/Locale";
import createPersistedState from "vuex-persistedstate";
import { persistedStateOptions } from "./plugins/vuex-persistedstate.js";

Vue.use(Vuex);

/**
 * @global these variables and methods are all global.
 * They can be accessed anywhere using mapState, mapGetters & mapMutations.
 * @tutorial https://vuex.vuejs.org/guide/getters.html#the-mapgetters-helper
 */
export default new Vuex.Store({
  plugins: [createPersistedState(persistedStateOptions)],

  state: {
    // Current locale code (e.g., `es-EC`, `en-US`) (This line doesn't actually alter the default language, see ui/src/App.vue).
    currentLocale: new Locale("en-US"),

    // All available I18NLocale instances (locale and description).
    localeModels: [],

    // Current `Account` object if someone logged in.
    currentAccount: null,

    // Current JSON Web Token if someone logged in.
    currentJWT: null,

    // All translations for the currentLocale.
    translations: [],
  },

  getters: {
    /**
     * @name isLoggedIn
     * @function
     * @param {*} state vuex passes "state" automatically
     * @yields {Object} describing the current Account
     */
    isLoggedIn(state) {
      return state.currentJWT && state.currentAccount;
    },

    /**
     * @name currentLocaleModel
     * @function
     * @param {*} state vuex passes "state" automatically
     * @yields {Object} describing the current Language & Locale
     */
    currentLocaleModel(state) {
      return state.localeModels.find(
        (localeModel) =>
          localeModel.locale.languageCode === state.currentLocale.languageCode
      );
    },

    /**
     * @name currentLanguageCode
     * @function
     * @param {*} state vuex passes "state" automatically
     * @yields {Object} describing the current Language
     */
    currentLanguageCode(state) {
      const currentLocaleModel = state.localeModels.find(
        (localeModel) =>
          localeModel.locale.languageCode === state.currentLocale.languageCode
      );
      if (currentLocaleModel) {
        return currentLocaleModel.languageCode;
      } else {
        throw Error("No current language code");
      }
    },
  },

  mutations: {
    /**
     * @name logIn
     * @function
     * @param {*} state vuex passes "state" automatically
     * @param {Object} payload containing login information
     */
    logIn(state, payload) {
      state.currentAccount = payload.account;
      state.currentJWT = payload.jwt;
      setJWT(payload.jwt);
    },

    /**
     * @name logOut
     * @function
     * @param {*} state vuex passes "state" automatically
     */
    logOut(state) {
      state.currentAccount = null;
      state.currentJWT = null;
    },

    /**
     * @name setCurrentLocale
     * @function
     * @param {*} state vuex passes "state" automatically
     * @param {Object} locale
     */
    setCurrentLocale(state, locale) {
      state.currentLocale = locale;
    },

    /**
     * @name setLocaleModels
     * @function
     * @param {*} state vuex passes "state" automatically
     * @param {Object} inputLocaleModels
     */
    setLocaleModels(state, inputLocaleModels) {
      state.localeModels = inputLocaleModels.map(
        (inputLocaleModel) => new LocaleModel(inputLocaleModel)
      );
    },
  },
});
