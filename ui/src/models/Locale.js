/**
 * @file
 * @name Locale.js
 * @exports ../App.vue
 * @exports ../store.js
 * @exports ../layouts/app-bars/ArcoAppBar.vue
 * @exports ../layouts/app-bars/StandardAppBar.vue
 * @exports ../plugins/vuex-persistedstate.js
 * Creates the Locale object for managing language and locale.
 */

export function assertValidLocaleString(localeString) {
  if (!/^[a-z]{2}-[A-Z]{2}$/.test(localeString)) {
    throw Error(`Invalid locale '${JSON.stringify(localeString)}'`);
  }
}

// Convert a single character of a country code to its Unicode regional indicator.
function charToRegionalIndicator(char) {
  const regionalIndicatorA = 0x1f1e6;
  const ch = char.toUpperCase();

  if (ch < "A" || ch > "Z") {
    throw Error(`Invalid character '${char}'`);
  } else {
    return ch.charCodeAt(0) - "A".charCodeAt(0) + regionalIndicatorA;
  }
}

// Convert all the characters in a string to their Unicode regional indicator.
function strToRegionalIndicator(str) {
  const values = str.split("").map((ch) => charToRegionalIndicator(ch));
  return String.fromCodePoint(...values);
}

export class Locale {
  constructor(localeString) {
    assertValidLocaleString(localeString);

    const [languageCode, countryCode] = localeString.split("-");
    this.languageCode = languageCode;
    this.countryCode = countryCode;
  }

  toString() {
    return `${this.languageCode}-${this.countryCode}`;
  }

  get flag() {
    return strToRegionalIndicator(this.countryCode.toUpperCase());
  }

  static fromObject(obj) {
    return new Locale(`${obj.languageCode}-${obj.countryCode}`);
  }
}

export class LocaleModel {
  constructor(i18NLocale) {
    this.locale = new Locale(i18NLocale.code);
    this.description = i18NLocale.desc;
  }

  get languageCode() {
    return this.locale.languageCode;
  }

  get countryCode() {
    return this.locale.countryCode;
  }

  get flagAndDescription() {
    return `${this.locale.flag} ${this.description}`;
  }

  get languageAndCountry() {
    return this.locale.toString();
  }
}
