import Vue from "vue";
import App from "./App.vue";

import router from "./router";
import store from "./store";

import "./filters";

import vuetify from "./plugins/vuetify";
import "./plugins/axios";
import i18n from "./plugins/vue-i18n";
import "./plugins/google-maps";

const app = new Vue({
  vuetify,
  store,
  router,
  i18n,
  render: (h) => h(App),
}).$mount("#app");

if (window.Cypress) {
  // let cypress have access to the vue instance
  console.log("cypress detected");
  window.app = app;
} else {
  console.log("Cypress not detected");
}
