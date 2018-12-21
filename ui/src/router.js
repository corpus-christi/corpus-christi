// Vue Router configuration

import Vue from "vue";
import VueRouter from "vue-router";

import Locale from "./pages/Locale.vue";
import Home from "./pages/Home.vue";
import People from "./pages/People";

Vue.use(VueRouter);
const router = new VueRouter({
  mode: "history",
  routes: [
    { name: "home", path: "/", component: Home },
    { name: "people", path: "/people", component: People },
    { name: "locale", path: "/locale", component: Locale }
  ]
});

export default router;
