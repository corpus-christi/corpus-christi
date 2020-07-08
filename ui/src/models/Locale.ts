export function assertValidLocaleString(localeString: string) {
  if (!/^[a-z]{2}-[A-Z]{2}$/.test(localeString)) {
    throw Error(`Invalid locale '${JSON.stringify(localeString)}'`);
  }
}

// Convert a single character of a country code to its Unicode regional indicator.
function charToRegionalIndicator(char: string) {
  const regionalIndicatorA = 0x1f1e6;
  const ch = char.toUpperCase();

  if (ch < "A" || ch > "Z") {
    throw Error(`Invalid character '${char}'`);
  } else {
    return ch.charCodeAt(0) - "A".charCodeAt(0) + regionalIndicatorA;
  }
}

// Convert all the characters in a string to their Unicode regional indicator.
function strToRegionalIndicator(str: string) {
  const values = str.split("").map((ch) => charToRegionalIndicator(ch));
  return String.fromCodePoint(...values);
}

export class Locale {
  public readonly languageCode: string;
  public readonly countryCode: string;

  constructor(localeString: string) {
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

  static fromObject(obj: { languageCode: String; countryCode: String }) {
    return new Locale(`${obj.languageCode}-${obj.countryCode}`);
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
  public readonly locale: Locale;
  public readonly description: string;

  constructor(i18NLocale: I18NLocale) {
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
}
