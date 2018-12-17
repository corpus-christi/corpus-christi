import Vue from 'vue'
import VueI18n from 'vue-i18n'

Vue.use(VueI18n);

const messages = {
    en: {
        message: {
            foo: 'Foo, my friend!'
        }
    },
    es: {
        message: {
            foo: 'Foo, mi amigo!'
        }
    }
};

const i18n = new VueI18n({
    locale: 'es',
    messages
});

export default i18n;
