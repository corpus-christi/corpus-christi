import Vue from "vue";

import router from './router';
import './plugins/vuetify';

import App from "./App.vue";

new Vue({
    el: "#app",
    router,
    render: h => h(App)
});
