# Data Dictionary

## Conventions

1. Almost all primary keys are simply auto-incrementing integer fields called `id`.
   A few tables have primary keys called `code`
1. Foreign keys have a name like `<table>_<pk>`,
   where `<table>` is the name of the table at the end of the relationship
   and `<pk>` is that name of `<table>`'s primary key.
   For example, `location_id` is the name of a foreign key to the `location` table,
   which has a primary key called `id`.
1. Column types are indicated using standard SQL types _or_ 
   names of types defined in `corpus-christi/api/shared/models.py`.
1. In the following, attributes whose purpose is self evident are not documented.
1. Associative tables (for many-to-many relationships) have at least two foreign key
   fields that are _also_ parts of a composite primary key to ensure no duplicate
   relationships are stored.
1. Common fields that appear in multiple tables:
   - The `active` flag indicates that its containing entity is active;
     the main purpose of this field is to allow CC to "delete" an entity instance
     without actually removing it. We don't _delete_, we _deactivate_.

## I18N

CC is pervasively internationalized.
Two terms are important to keep in mind (and to keep straight):

1. _Internationalization_ (in software at least) refers to creating code
   that makes it easy to render output to the user in various human languages.
   The term is often abbreviated _I18N_ (it starts with `I`, ends with `N`,
   and has 18 other letters in the middle).
   Code that has been internationalized includes unique identifiers
   (sometimes words in a natural language, sometimes other identifiers)
   that stand as place holders for translations into a particular human language.
1. The partner of I18N is _Localization_ (similarly abbreviated _L10N_).
   This term refers to creating the translations themselves in a specific natural language.
   For each identifier in I18N-friendly code,
   a translator provides the appropriate natural language 
   text (often called a _gloss_). 
   The end-user sees the localized translation while using the application.

We use ISO standard abbreviations for languages and country.

1. An _I18N Locale_ is keyed with a locale code,
   a five-character code
   that combines a two-letter ISO _language code_ (e.g., `es` for Espanol)
   and a two-letter ISO _country code_ (e.g., `EC` for Ecuador)
   using an intermediate underscore (e.g., `es_EC` for Ecuadorian Spanish).
   By ISO convention,
   the language code is always two lower-case letters
   and the country code is always two upper-case letters.
   The combination of language and country allows the locale to express
   country-specific variations in the language
   (e.g., there is `en_US` for US English and `en_GB` for English in Great Britain).
1. An _I18N Key_ is a CC-specific identifier for text that can be localized
   (refer to the discussion on I18N, above).
   By convention, keys in CC are "dotted" to express a hierarchy.
   For example, `person.name.first` is the identifier in the code
   that indicates "Person's first name here."
   These keys appear in the `code` attribute of _I18N Key_.
   There is also an optional `description` attribute that 
   can be used to provide details about the purpose or meaning
   of the `code` for the convenience of the human translator.
1. The _I18N Value_ implements an many-to-many relationship 
   between _I18N Locale_ and _I18N Key_.
   - The `gloss` attribute stores the string for the given key
     in the given locale (e.g., `person.name.first` in `es_EC`).
     
Where CC uses I18N, the _code_ specifies the _I18N Key_.
The locale is determined by a browser-wide setting.
When rendering a localized string,
CC uses the key from the code and the locale from the browser
to determine the appropriate gloss to render at that portion of the page.
   
## People

1. _Person_ contains personal (!) information about every individual in CC.
   The _majority_ of people in the system cannot log in or interact with the system
   in any way other than as a public user.
1. An _Account_ grants a _Person_ the ability to log in and interact with CC.
   -  CC implements a `username` because not all people who will interact with the system
      will have email addresses.
   - The `password` field is stored as an appropriately salted and encrypted hash value.
1. In addition to the normal fields for a _Person_, each _Person_ can have additional
   attributes (e.g., marital status). CC assumes such attributes have discrete values
   (i.e., something shown with radio buttons or a drop-down list as opposed to free-form text input)
   and that attributes and attribute values will change over time.
   - The _Attribute_ table stores the name of an attribute (e.g., `Martial Status`).
   - _Attribute_ has a one-to-many relationship with the _Attribute Value_ table,
     which stores the possible values for that attribute (e.g., `Single`, `Married`, `Divorced`).
   - _Person Attribute_ associates a _Person_ with specific _Attribute Values_s
     (e.g., this _Person_ is `Single`).
   
## Places

## Groups

## Courses

## Events
