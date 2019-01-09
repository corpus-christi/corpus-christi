import Vue from "vue";
import Vuetify from 'vuetify'
import VeeValidate from "vee-validate";	
import VueI18n from "vue-i18n";

import i18n_data from "../../i18n/cc-i18n.json";

Vue.use(VueI18n);

const i18n = new VueI18n({
  locale: "es",
  messages: i18n_data
});

Vue.use(VeeValidate, {
  i18n
});

Vue.use(Vuetify, {
  lang: {
    t: (key, ...params) => i18n.t(key, params)
  }
});

export default i18n;
