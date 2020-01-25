export function assertValidLocaleString(localeString) {
  if (!/^[A-Za-z]{2}-[A-Za-z]{2}$/.test(localeString)) {
    throw Error(`Invalid locale '${JSON.stringify(localeString)}'`);
  }
}

// Convert a single character of a country code to its Unicode regional indicator.
function charToRegionalIndicator(ch) {
  const regionalIndicatorA = 0x1f1e6;
  ch = ch.toUpperCase();

  if (ch < "A" || ch > "Z") {
    return "X";
  } else {
    return ch.charCodeAt(0) - "A".charCodeAt(0) + regionalIndicatorA;
  }
}

// Convert all the characters in a string to their Unicode regional indicator.
function strToRegionalIndicator(str) {
  const values = str.split("").map(ch => charToRegionalIndicator(ch));
  return String.fromCodePoint.apply(null, values);
}

export class Locale {
  constructor(localeString) {
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

export class LocaleModel {
  constructor(localeModel) {
    this._locale = new Locale(localeModel.code);
    this._description = localeModel.desc;
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
