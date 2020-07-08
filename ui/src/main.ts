import Vue from "vue";

import router from "./router";
import store from "./store";

import "./filters";

import "./plugins/vuetify";
import "./plugins/axios";
import i18n from "./plugins/vue-i18n";
import "./plugins/google-maps";

import App from "./App.vue";

const app = new Vue({
  el: "#app",
  store: store,
  router: router,
  i18n: i18n,
  render: (h) => h(App),
});

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
