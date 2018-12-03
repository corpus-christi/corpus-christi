import Vue from "vue";

import Vuetify from "vuetify";
import "vuetify/dist/vuetify.min.css";
import "material-design-icons-iconfont/dist/material-design-icons.css";

import Locale from "./pages/Locale.vue";
import Home from './pages/Home.vue';

import VueRouter from "vue-router";
import App from "./App.vue";

Vue.use(Vuetify);
Vue.use(VueRouter);
const router = new VueRouter({
    mode: "history",
    routes: [
        {name: 'home', path: '/', component: Home},
        {name: "locale", path: "/locale", component: Locale}
    ]
});

new Vue({
    el: "#app",
    router,
    render: h => h(App)
});
