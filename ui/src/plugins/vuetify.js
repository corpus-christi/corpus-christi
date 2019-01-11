import Vue from "vue";
import Vuetify from "vuetify/lib";
import i18n from "./vue-i18n";
import "vuetify/src/stylus/app.styl";
import "material-design-icons-iconfont/dist/material-design-icons.css";

Vue.use(Vuetify, {
  iconfont: "md",
  lang: {
    t: (key, ...params) => i18n.t(key, params)
  }
});
