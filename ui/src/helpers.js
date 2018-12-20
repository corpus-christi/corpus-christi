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
  const vals = str.split("").map(ch => charToRegionalIndicator(ch));
  return String.fromCodePoint.apply(null, vals);
}

// Convert a two-letter country code into the Unicode characters for its flag_unicode.
export function flagForCountry(countryCode) {
  countryCode = countryCode.toUpperCase();

  if (/^[A-Z]{2}$/.test(countryCode)) {
    return strToRegionalIndicator(countryCode);
  } else {
    return strToRegionalIndicator("XX");
  }
}

// Convert a locale code (e.g., `en-US`) to the Unicode for its flag.
export function flagForLocale(localeCode) {
  if (localeCode.length === 5) {
    const country_code = localeCode.split("-")[1];
    return flagForCountry(country_code);
  } else {
    const genericFlag = 0x1f6a9;
    return String.fromCodePoint(genericFlag);
  }
}

// Split locale code into language and country codes.
export function splitLocaleCode(locale_code) {
  const [languageCode, countryCode] = locale_code.split("-");
  return {
    languageCode,
    countryCode
  };
}
