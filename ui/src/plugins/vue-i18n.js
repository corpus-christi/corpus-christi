import Vue from "vue";
import VueI18n from "vue-i18n";

import VeeValidate from "vee-validate";
import enValidation from "vee-validate/dist/locale/en";
import esValidation from "vee-validate/dist/locale/es";

Vue.use(VueI18n);

const i18n = new VueI18n({
  locale: "es-EC",
  fallbackLocale: "en-US",
  silentTranslationWarn: true, // Let warnings through.
});

Vue.use(VeeValidate, {
  i18n,
  i18nRootKey: "i18n_data",
  dictionary: {
    "en-US": {
      messages: enValidation.messages,
    },
    "es-EC": {
      messages: esValidation.messages,
    },
  },
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
