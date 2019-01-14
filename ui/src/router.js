// Vue Router configuration

import Vue from "vue";
import VueRouter from "vue-router";
import store from "./store";

Vue.use(VueRouter);

const router = new VueRouter({
  mode: "history",
  routes: [
    {
      name: "public",
      path: "/",
      meta: { layout: "arco" },
      component: () => import("@/pages/Public")
    },
    {
      name: "login",
      path: "/login",
      meta: { layout: "arco" },
      component: () => import("@/pages/Login")
    },
    {
      name: "admin",
      path: "/admin",
      meta: { authRequired: true },
      component: () => import("@/pages/Admin")
    },
    {
      name: "people",
      path: "/people",
      meta: { authRequired: true },
      component: () => import("@/pages/People")
    },
    {
      name: "groups",
      path: "/groups",
      meta: { authRequired: true },
      component: () => import("@/pages/Groups")
    },
    {
      name: "locale",
      path: "/locale",
      meta: { authRequired: true },
      component: () => import("@/pages/Locale")
    }
  ]
});

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.authRequired)) {
    // The destination requires authentication.
    if (store.getters.isLoggedIn) {
      // But we're already logged in.
      next();
    } else {
      // So redirect to the login page; retain
      // the desired page for a later redirect.
      next({
        name: "login",
        query: { redirect: to.name }
      });
    }
  } else {
    // The destination doesn't require authentication.
    next();
  }
});

export default router;
