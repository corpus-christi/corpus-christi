// Vuex store; contains global state information for the entire UI.

import Vue from "vue";
import Vuex from "vuex";
import Account from "./models/Account";
import { setJWT } from "./plugins/axios";

Vue.use(Vuex);

const JWT_KEY = "cc-jwt";
const ACCOUNT_KEY = "cc-account";

export default new Vuex.Store({
  state: {
    // Current locale code (e.g., `es-EC`, `en-US`)
    currentLocaleCode: "es-EC",
    // All available locales.
    locales: [],

    // Current `Account` object if someone logged in.
    _currentAccount: null,
    // Current JSON Web Token if someone logged in.
    _currentJWT: null,

    // All translations for the given currentLocaleCode
    translations: []
  },

  getters: {
    // Return the current JWT; refresh from local storage if necessary.
    currentJWT(state) {
      if (!state._currentJWT) {
        state._currentJWT = localStorage.getItem(JWT_KEY);
      }
      return state._currentJWT;
    },

    // Return the current account; refresh from local storage if necessary.
    currentAccount(state) {
      if (!state._currentAccount) {
        const acct_json = localStorage.getItem(ACCOUNT_KEY);
        if (acct_json) {
          const { username, firstName, lastName } = JSON.parse(acct_json);
          state._currentAccount = new Account(username, firstName, lastName);
        }
      }
      return state._currentAccount;
    },

    // Is there a currently logged-in user?
    isLoggedIn(state, getters) {
      return getters.currentJWT && getters.currentAccount;
    },

    currentLocale(state) {
      return state.locales.find(loc => loc.code === state.currentLocaleCode);
    },

    currentLanguageCode(state, getters) {
      const current = getters.currentLocale;
      if (current) {
        return current.code.split("-")[0];
      } else {
        return "";
      }
    }
  },

  mutations: {
    logIn(state, payload) {
      state._currentAccount = payload.account;
      state._currentJWT = payload.jwt;
      setJWT(payload.jwt);
      localStorage.setItem(JWT_KEY, payload.jwt);
      localStorage.setItem(ACCOUNT_KEY, JSON.stringify(payload.account));
    },

    logOut(state) {
      state._currentAccount = null;
      state._currentJWT = null;
      localStorage.removeItem(JWT_KEY);
      localStorage.removeItem(ACCOUNT_KEY);
    },

    setCurrentLocaleCode(state, code) {
      state.currentLocaleCode = code;
    },

    setLocales(state, locales) {
      state.locales = locales;
    }
  }
});
