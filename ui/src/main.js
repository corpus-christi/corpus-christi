import Vue from "vue";

import VCharts from "v-charts";

import router from "./router";
import store from "./store";

import "./plugins/vuetify";
import "./plugins/axios";
import i18n from "./plugins/vue-i18n";
import "./plugins/google-maps";

import App from "./App.vue";

Vue.use(VCharts);

new Vue({
  el: "#app",
  store: store,
  router: router,
  i18n: i18n,
  render: h => h(App)
});
