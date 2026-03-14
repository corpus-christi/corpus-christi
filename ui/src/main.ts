import { createApp } from "vue";
import { createPinia } from "pinia";

import router from "./router";
import i18n from "./plugins/vue-i18n";
import vuetify from "./plugins/vuetify";
import axiosPlugin from "./plugins/axios";
import googleMapsPlugin from "./plugins/google-maps";

import App from "./App.vue";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(i18n);
app.use(vuetify);
app.use(axiosPlugin);
app.use(googleMapsPlugin);

app.mount("#app");
