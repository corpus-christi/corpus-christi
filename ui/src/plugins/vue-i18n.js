import Vue from "vue";
import VeeValidate from "vee-validate";
import VueI18n from "vue-i18n";
import enValidation from "vee-validate/dist/locale/en";
import esValidation from "vee-validate/dist/locale/es";

import i18n_data from "../../i18n/cc-i18n.json";

Vue.use(VueI18n);

const i18n = new VueI18n({
  locale: "es-EC",
  fallbackLocale: "en-US",
  messages: i18n_data,
  silentTranslationWarn: true // Let warnings through.
});

Vue.use(VeeValidate, {
  i18n,
  i18nRootKey: "i18n_data",
  dictionary: {
    "en-US": {
      messages: enValidation.messages,
      attributes: i18n_data["en-US"].validation.attributes
    },
    "es-EC": {
      messages: esValidation.messages,
      attributes: i18n_data["es-EC"].validation.attributes
    }
  }
});

export function getResponseErrorKey(statusCode) {
  if (statusCode >= 500) return "error-report.error-types.error-5xx";
  else if (statusCode >= 400)
    switch (statusCode) {
      case 400:
        return "error-report.error-types.error-400";
      case 401:
        return "error-report.error-types.error-401";
      case 404:
        return "error-report.error-types.error-404";
      default:
        return "error-report.error-types.error-4xx";
    }
  else {
    throw new RangeError(
      `status code ${statusCode} does not correspond to an error`
    );
  }
}

export default i18n;
