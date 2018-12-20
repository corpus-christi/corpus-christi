import Vue from "vue";
import VueI18n from "vue-i18n";

Vue.use(VueI18n);

const messages = {
  en: {
    page: {
      title: "Our Home Page"
    }
  },
  es: {
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
