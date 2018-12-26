// Vuex store; contains global state information for the entire UI.

import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    currentLocaleCode: "", // Current locale code
    locales: [], // All available locales

    currentAccount: null,
    currentJWT: null
  },
  getters: {
    currentLocale: state => {
      return state.locales.find(loc => loc.code === state.currentLocaleCode);
    },

    currentLanguageCode: (state, getters) => {
      const current = getters.currentLocale;
      if (current) {
        return current.code.split("-")[0];
      } else {
        return "";
      }
    }
  },
  mutations: {
    setCurrentLocaleCode(state, code) {
      state.currentLocaleCode = code;
    },

    setLocales(state, locales) {
      state.locales = locales;
    },

    setCurrentAccount(state, account) {
      state.currentAccount = account;
    },

    setCurrentJWT(state, jwt) {
      state.currentJWT = jwt;
    }
  }
});
