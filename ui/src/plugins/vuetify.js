/**
 * @file
 * @name vuetify.js
 * Creates the Vuetify object which runs the site's asthetics.
 * @todo Add comments describing where this file's imported to.
 */
import Vue from "vue";
import Vuetify from "vuetify/lib";
import i18n from "./vue-i18n";
// import "material-design-icons-iconfont/dist/material-design-icons.css";
// import "vuetify/dist/vuetify.min.css";

Vue.use(Vuetify);

export default new Vuetify({
  icons: {
    iconfont: "md",
  },
  lang: {
    t: (key, ...params) => i18n.t(key, params),
  },
});
