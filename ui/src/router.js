// Vue Router configuration

import Vue from "vue";

import Locale from "./pages/Locale.vue";
import Home from './pages/Home.vue';

import VueRouter from "vue-router";

Vue.use(VueRouter);
const router = new VueRouter({
    mode: "history",
    routes: [
        {name: 'home', path: '/', component: Home},
        {name: "locale", path: "/locale", component: Locale}
    ]
});

export default router;
