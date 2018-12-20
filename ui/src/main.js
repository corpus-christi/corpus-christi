import Vue from "vue";

import router from "./router";
import store from "./store";

import "./plugins/vuetify";
import i18n from "./plugins/vue-i18n";

import App from "./App.vue";

new Vue({
  el: "#app",
  store: store,
  router: router,
  i18n: i18n,
  render: h => h(App)
});
