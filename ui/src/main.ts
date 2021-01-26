/**
 * @file The Main File.
 * Pulls everything together and creates the primary Vue Object.
 * Auto-injects into 'ui/public/index.html'
 */

import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import vuetify from "./plugins/vuetify";
import i18n from "./plugins/vue-i18n";

import "./filters";

import "./plugins/axios";
import "./plugins/google-maps";

const app = new Vue({
  router,
  store,
  vuetify,
  i18n,
  render: (h) => h(App),
}).$mount("#app");

declare global {
  interface Window {
    Cypress: any;
    app: Vue;
  }
}

if (window.Cypress) {
  // let cypress have access to the vue instance
  console.log("cypress detected");
  window.app = app;
} else {
  console.log("Cypress not detected");
}
