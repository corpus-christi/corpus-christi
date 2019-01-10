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
     in the given locale (e.g., `person.name.first` in `es_EC`
     might be `Nombre de pila`, but in `en_US` would be `First Name`).
   - `verified` (initial value false) indicates that a native speaker of the target
     language has verified the `gloss` is correct and appropriate.
     
Where CC uses I18N, the _code_ specifies the _I18N Key_.
The locale is determined by a browser-wide setting.
When rendering a localized string,
CC uses the key from the code and the locale from the browser
to determine the appropriate gloss to render at that portion of the page.

Finally, the _Language_ table maps a language code (e.g., `de`)
to the localized name for that language (e.g., in `en_US`,
the gloss would be `German`, but in `de`, it would be `Deutsch`).
   
## People

1. _Person_ contains personal (!) information about every individual in CC.
   The _majority_ of people in the system cannot log in or interact with the system
   in any way other than as a public user.
1. In addition to the normal fields for a _Person_, each _Person_ can have additional
   attributes (e.g., marital status or birth date).
   CC allows attributes to take one of two forms:
   1. An _enumerated attribute_ can take one of a discrete set of values.
      For example, `Marital Status` may be `Single`, `Married`, `Divorced`, etc.
      Instances of _Attribute Value_ store each possible value for an 
      enumerated attribute.
   1. A _string attribute_ stores an arbitrary text value.
      For example, a `Birth Date` attribute should allow entry of a string containing a date.
      The UI should constrain the values of string attributes to conform to a specific format
      a appropriate.

   The _Attribute_ table stores:
   - `name_i18n`, the name of the attribute (e.g., `Martial Status`)
   - `type_i18n`, the type of the attribute (e.g, enumerated type, date, number)
   
   The _Attribute Value_ entity stores the list of values that an enumerated attribute can take.
   
   A _Person Attribute_ associates a _Person_ with an attribute value.
   - `enum_value` is used for enumerated attributes and contains the key 
     of an _Attribute Value_.
   - `string_value` stores string attributes directly.
   Exactly one of `enum_value` and `string_value` should be set
   in any instance of _Person Attribute_.

   All attribute names and values are stored as _I18N Key_'s,
   so that they can be localized.
1. An _Account_ grants a _Person_ the ability to log in and interact with CC.
   -  CC implements a `username` because not all people who will interact with the system
      will have an email address.
   - The `password_hash` field contains a salted and encrypted hash of the user's actual password.
1. For authorization, CC associates each _Account_ with one or more _Role_'s.
   _Role_'s determine what this _Account_ is allowed to do in CC.
   Roles are simple (I18N) names that are associated
   many-to-many with _Account_ by the _Account Role_ table.
   Code in the system that needs to determine whether the current user
   can perform some action (e.g., create a new group, set up a training course)
   checks for a specific _Role_ among those associated with the current _Account_.
1. CC supports hierarchical relationships between _Person_'s. 
   The _Manager_ entity supports a simple tree structure of _Person_ instances.
   - `person_id` refers to a specific person who is a _Manager_.
   - `manager_id` is a self-referential attribute that indicates
     this _Manager_'s _Manager_.
   - `description` is a localizable field to describe each participant in the hierarchy.
   
   For example: each _Group_ has a group leader, 
   and each group leader is supervised by a group overseer,
   who is responsible for multiple group leaders and their groups.
   This hierarchy could be represented as follows:
   ```
   Group -> Manager ("Group leader") -> Person
                                     -> Manager ("Group overseer") -> Person
   ```
   where the `description` of each `Manager` appears in parentheses.
   Multiple "Group leader" _Manager_ instances
   may refer to the same "Group overseer" _Manager_.

## Places

1. The _Address_ table provides fairly generic storage of a street address.
   It is intentionally generic to accommodate the wide variety of addresses
   encountered in practice.
   - `name` is an optional field that gives the address a name (e.g., 'Arco Iglesia Christiana`)
   - `address` is the street address (e.g., `Avenida Loja`)
   - `city` is the city or town of the address (e.g., `Cuenca`)
   - `area_id` is a foreign key to an _Area_; refer to its documentation, below
   - `latitude`, `longitude` pinpoint a location that doesn't have a street address.
     These attributes can be used with or without a street address.
1. An _Area_ is a generic table that stores place information that is larger than a city
   but smaller than a country. For example, in the United States, it would typically be 
   a state (e.g., `Indiana`) and in Ecuador, it might be a province (e.g., `Azuay`).
1. A _Country_ is keyed using an ISO standard country code. It's value is an _I18N Key_
   that allows country names to be localized.
1. A _Location_ stores a particular location _within_ an _Address_.
   For example, `description` might contain `Main Auditorium`, `Classroom 040`, etc.

Note that _Address_ and _Area_ do not include an _I18N Key_.
We assume that they will always be a localized value
for which translation to another language will be unnecessary.
   
## Groups

These tables maintain data for home churches/small groups.

1. _Group_ stores details about a single group.
   - `description` should be a high-level description of the group,
     including its intended membership. This information will be visible
     on the public home group map.
   - `manager_id` refers to the _Manager_ that refers to
     the _Person_ who leads this group.
     Refer to the discussion of the _Manager_ entity.
1. A _Member_ is a _Person_ who is part of a _Group_. 
1. A _Meeting_ is a single gathering of a _Group_ 
   at a particular time and place.
1. An _Attendance_ instance indicates 
   that a _Member_ attended a _Meeting_ of the _Group_.

## Courses

Tables in this group record data about training courses.

1. The _Course_ is the central table for this group.
   It stores the details of a particular course 
   - `name` is the course name (e.g., `Introduction to Christianity`)
   - `description` contains more details about the course.
1. A _Course_ can have one or more _Prerequisites_ courses.
1. A _Course Offering_ is an instance of the course being taught.
   - `notes` stores clarifying details of this course
   - `max_size` is the maximum number of students who can be enrolled in this course
1. Several _Class Meetings_ will be part of any _Course Offering_.
   Each meeting takes places at a specific location and time.
   Different meetings may have different teachers.
1. A _Student_ enrolls in a _Course Offering_.
   Students may [self-register](#self-registration).
1. _Class Attendance_ indicates that a _Student_ attended a _Class Meeting_.
   To receive credit for the course, a _Student_ must attend _all_ meetings.
1. Completing multiple courses may lead to a _Diploma_.
1. A _Diploma Course_ instance indicates that a _Course_ is required for a _Diploma_.
1. CC creates a _Diploma Awarded_ instance when a _Student_ completes all the _Course_'s required for a _Diploma_,

## Events

An _event_ is a planned activity with a location, scheduled time, participants, etc.

1. The _Event_ table is the central table for this module
   (e.g., Fall men's retreat, Sunday worship service)
   - `start` and `end` are both `datetime` fields,
     allowing an _Event_ to span multiple days if required.
   
1. An _Event_ can be associated with assets, teams, or individual people. 
1. An _Asset_ is a non-personal resource needed to conduct an _Event_.
   Examples include: a room in the church, sound equipment, video projector,
   screen, chairs, tables, etc.
   - `location_id` can connect an _Asset_ with a _Location_,
     intended to be the location where that _Asset_ can normally be found
     (e.g., `Storage Room 2`)
     
1. The _Event Asset_ table connects an _Event_ to an _Asset_.
1. A _Team_ is an identified group of _Person_'s (e.g., a worship team).
1. The _Event Team_ table connects an _Event_ to a _Team_.
1. A _Team Member_ instance connects a _Team_ with a _Person_ on the team.
1. An _Event Person_ is an individual (not a team) who is part of
   the _Event_ (e.g., `Keynote speaker`).
1. An _Event Participant_ is a _Person_
   who has signed up to participate in an _Event_.
   Participants may [self-register](#self-registration).
