import Vue from "vue";

import router from "./router";
import store from "./store";

import "./filters";

import "./plugins/vuetify";
import "./plugins/axios";
import i18n from "./plugins/vue-i18n";
import "./plugins/google-maps";

import App from "./App.vue";

new Vue({
  el: "#app",
  store: store,
  router: router,
  i18n: i18n,
  render: h => h(App)
});
