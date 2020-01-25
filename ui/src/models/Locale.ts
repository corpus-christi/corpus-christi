export function assertValidLocaleString(localeString: string) {
  if (!/^[A-Za-z]{2}-[A-Za-z]{2}$/.test(localeString)) {
    throw Error(`Invalid locale '${JSON.stringify(localeString)}'`);
  }
}

// Convert a single character of a country code to its Unicode regional indicator.
function charToRegionalIndicator(char: string) {
  const regionalIndicatorA = 0x1f1e6;
  const ch = char.toUpperCase();

  if (ch < "A" || ch > "Z") {
    return "X";
  } else {
    return ch.charCodeAt(0) - "A".charCodeAt(0) + regionalIndicatorA;
  }
}

// Convert all the characters in a string to their Unicode regional indicator.
function strToRegionalIndicator(str: string) {
  const values = str.split("").map(ch => charToRegionalIndicator(ch));
  return String.fromCodePoint.apply(values);
}

export class Locale {
  private _languageCode: string;
  private _countryCode: string;
  constructor(localeString: string) {
    assertValidLocaleString(localeString);

    const [languageCode, countryCode] = localeString.split("-");
    this._languageCode = languageCode;
    this._countryCode = countryCode;
  }

  toString() {
    return `${this._languageCode}-${this._countryCode}`;
  }

  get languageCode() {
    return this._languageCode;
  }

  get countryCode() {
    return this._countryCode;
  }

  get flag() {
    return strToRegionalIndicator(this.countryCode.toUpperCase());
  }
}

export interface I18NValueSchema {
  key_id: string;
  locale_code: string;
  gloss: string;
}

export interface I18NLocale {
  code: string;
  desc: string;
}

export class LocaleModel {
  private _locale: Locale;
  private _description: string;

  constructor(i18NLocale: I18NLocale) {
    this._locale = new Locale(i18NLocale.code);
    this._description = i18NLocale.desc;
  }

  get locale() {
    return this._locale;
  }

  get languageCode() {
    return this._locale.languageCode;
  }

  get countryCode() {
    return this._locale.countryCode;
  }

  get description() {
    return this._description;
  }

  get flagAndDescription() {
    return this._locale.flag + this.description;
  }
}
