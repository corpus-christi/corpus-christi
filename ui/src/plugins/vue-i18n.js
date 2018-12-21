import Vue from "vue";
import VeeValidate from "vee-validate";
import VueI18n from "vue-i18n";
import enValidation from "vee-validate/dist/locale/en";
import esValidation from "vee-validate/dist/locale/es";

const messages = {
  en: {
    message: {
      hello: "Enter a new person"
    },
    label: {
      email: "Email",
      phone: "Phone",
      date: {
        birthday: "Birthday"
      },
      name: {
        first: "First Name",
        last: "Last Name"
      },
      gender: {
        male: "Male",
        female: "Female"
      }
    },
    common: {
      required: "Required"
    },
    page: {
      title: "Our Home Page"
    }
  },
  es: {
    message: {
      hello: "Entrar nueva persona"
    },
    common: {
      required: "Necesario"
    },
    label: {
      email: "Correo electrónico",
      phone: "Teléfono",
      date: {
        birthday: "Cumpleaños"
      },
      name: {
        first: "Nombre de pila",
        last: "Apellido"
      },
      gender: {
        female: "Mujer",
        male: "Hombre"
      }
    },
    page: {
      title: "Nuestra Pagina de Inicio"
    }
  }
};

Vue.use(VueI18n);

const i18n = new VueI18n({
  locale: "es",
  messages
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
