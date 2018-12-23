import Vue from "vue";
import VeeValidate from "vee-validate";
import VueI18n from "vue-i18n";
import enValidation from "vee-validate/dist/locale/en";
import esValidation from "vee-validate/dist/locale/es";

import i18n_data from "../../i18n/cc-i18n.json";

Vue.use(VueI18n);

const i18n = new VueI18n({
  locale: "es",
  messages: i18n_data
});

Vue.use(VeeValidate, {
  i18n,
  dictionary: {
    en: {
      messages: enValidation.messages,
      attributes: {
        firstName: "FIRST NAME",
        lastName: "LAST NAME"
      },
      custom: {
        firstName: {
          required: "You need a name here, boy.",
          max: "Too many characters"
        },
        lastName: {
          min: "Must be longer"
        }
      }
    },
    es: {
      messages: esValidation.messages,
      attributes: {
        firstName: "SPANISH FIRST NAME",
        lastName: "SPANISH LAST NAME"
      },
      custom: {
        firstName: {
          required: "Necesitas un nombre aquí, muchacho."
        }
      }
    }
  }
});

export default i18n;
