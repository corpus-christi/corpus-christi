// Pinia store; contains global auth and locale state for the entire UI.

import { defineStore } from "pinia";
import { ref, computed } from "vue";
import Account from "../models/Account";
import { setJWT } from "../plugins/axios";
import { Locale, LocaleModel, type I18NLocale } from "../models/Locale";

const JWT_KEY = "cc-jwt";
const ACCOUNT_KEY = "cc-account";

export const useAuthStore = defineStore("auth", () => {
  const currentLocale = ref(new Locale("es-EC"));
  const localeModels = ref<LocaleModel[]>([]);
  const _currentAccount = ref<Account | null>(null);
  const _currentJWT = ref<string | null>(null);

  const currentJWT = computed(() => {
    if (!_currentJWT.value) {
      _currentJWT.value = localStorage.getItem(JWT_KEY);
    }
    return _currentJWT.value;
  });

  const currentAccount = computed(() => {
    if (!_currentAccount.value) {
      const acctJson = localStorage.getItem(ACCOUNT_KEY);
      if (acctJson) {
        const { username, firstName, lastName } = JSON.parse(acctJson);
        _currentAccount.value = new Account(username, firstName, lastName);
      }
    }
    return _currentAccount.value;
  });

  const isLoggedIn = computed(() => !!currentJWT.value && !!currentAccount.value);

  const currentLocaleModel = computed(() =>
    localeModels.value.find(
      m => m.languageCode === currentLocale.value.languageCode
    )
  );

  const currentLanguageCode = computed(() => {
    if (currentLocaleModel.value) return currentLocaleModel.value.languageCode;
    throw new Error("No current language code");
  });

  function logIn(payload: { account: Account; jwt: string }) {
    _currentAccount.value = payload.account;
    _currentJWT.value = payload.jwt;
    setJWT(payload.jwt);
    localStorage.setItem(JWT_KEY, payload.jwt);
    localStorage.setItem(ACCOUNT_KEY, JSON.stringify(payload.account));
  }

  function logOut() {
    _currentAccount.value = null;
    _currentJWT.value = null;
    localStorage.removeItem(JWT_KEY);
    localStorage.removeItem(ACCOUNT_KEY);
  }

  function setCurrentLocale(locale: Locale) {
    currentLocale.value = locale;
  }

  function setLocaleModels(inputLocaleModels: I18NLocale[]) {
    localeModels.value = inputLocaleModels.map(m => new LocaleModel(m));
  }

  return {
    currentLocale,
    localeModels,
    currentJWT,
    currentAccount,
    isLoggedIn,
    currentLocaleModel,
    currentLanguageCode,
    logIn,
    logOut,
    setCurrentLocale,
    setLocaleModels
  };
});
