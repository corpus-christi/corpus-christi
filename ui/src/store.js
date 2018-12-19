// Vuex store; contains global state information for the entire UI.

import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

export default new Vuex.Store({
    state: {
        currentLocaleCode: '',    // Current locale code
        locales: []               // All available locales
    },
    getters: {
        currentLocale(state) {
            return state.locales.find(loc => loc.code === state.currentLocaleCode)
        }
    },
    mutations: {
        setCurrentLocaleCode(state, code) {
            state.currentLocaleCode = code;
        },
        setLocales(state, locales) {
            state.locales = locales;
        }
    }
});
