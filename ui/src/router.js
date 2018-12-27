// Vue Router configuration

import Vue from "vue";
import VueRouter from "vue-router";

Vue.use(VueRouter);

const router = new VueRouter({
  mode: "history",
  routes: [
    {
      name: "home",
      path: "/",
      meta: { layout: "arco" },
      component: () => import("@/pages/Home.vue")
    },
    {
      name: "login",
      path: "/login",
      component: () => import("@/pages/Login.vue")
    },
    {
      name: "people",
      path: "/people",
      component: () => import("@/pages/People")
    },
    {
      name: "locale",
      path: "/locale",
      component: () => import("@/pages/Locale.vue")
    }
  ]
});

export default router;
