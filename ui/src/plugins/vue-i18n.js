import Vue from "vue";
import VueI18n from "vue-i18n";

Vue.use(VueI18n);

const messages = {
  en: {
    message: {
      hello: "Enter a new person"
    },
    label: {
      name: {
        first: "First Name",
        last: "Last Name"
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
      name: {
        first: "Nombre de pila",
        last: "Apellido"
      }
    },
    page: {
      title: "Nuestra Pagina de Inicio"
    }
  }
};

const i18n = new VueI18n({
  locale: "es",
  messages
});

export default i18n;
