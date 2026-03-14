import { createI18n } from "vue-i18n";
import i18nData from "../../i18n/cc-i18n.json";

const i18n = createI18n({
  legacy: false, // Use Composition API mode
  locale: "es-EC",
  fallbackLocale: "en-US",
  messages: i18nData,
  silentTranslationWarn: true
});

export default i18n;
