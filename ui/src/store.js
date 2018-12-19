// Vuex store; contains global state information for the entire UI.

import Vue from 'vue'
import Vuex from 'vuex'
import axios from "axios";

Vue.use(Vuex);

export default new Vuex.Store({
    state: {
        currentLocaleCode: 'en-US',     // Current locale code
        locales: []                     // All available locales
    },
    getters: {},
    mutations: {
        setCurrentLocale(state, code) {
            state.currentLocaleCode = code;
        },
        setLocales(state, locales) {
            state.locales = locales;
        }
    },
    actions: {
        initApp({commit}) {
            // Do asynchronous initialization of the application
            // before anything really gets going.
            axios.get("/api/v1/i18n/locales").then(response => {
                commit('setLocales', response.data);
            });
        }
    }
});
