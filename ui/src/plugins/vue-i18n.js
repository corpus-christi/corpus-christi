import Vue from "vue";
import VeeValidate from "vee-validate";
import VueI18n from "vue-i18n";
import enValidation from "vee-validate/dist/locale/en";
import esValidation from "vee-validate/dist/locale/es";

import i18n_data from "../../i18n/cc-i18n.json";

Vue.use(VueI18n);

const i18n = new VueI18n({
  locale: "es",
  messages: i18n_data,
  silentTranslationWarn: true
});

Vue.use(VeeValidate, {
  i18n,
  i18nRootKey: "i18n_data",
  dictionary: {
    en: {
      messages: enValidation.messages,
      attributes: i18n_data.en.validation.attributes
    },
    es: {
      messages: esValidation.messages,
      attributes: i18n_data.es.validation.attributes
    }
  }
});

export default i18n;
