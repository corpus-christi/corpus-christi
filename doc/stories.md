# Terms

1. By **application** we mean the entire _Corpus Christi_ (CC) system, including
  the user interface, API, database, administrative tools, etc.
1. CC implements a design pattern commonly called a _Single Page Application_
  (or _SPA_). To avoid terminological confusion with the previous definition of
  _application_, we refer to the SPA portion of CC as either the **user
  interface** (commonly, the **UI**) or the **web app**.
1. CC currently consists of several cooperating subsystems that address
   a single, reasonably coherent aspect of church management.
   We refer to these subsystems as **modules**.
   Initially, CC contains the following modules:

    1. `groups` - Home church/small group management and tracking
    1. `courses` - Teaching ministry management
    1. `events` - Event planning and registration
    1. `calendars` - Planning and calendaring

   A _module_ is intended to encompass standalone functionality
   that can optionally be used by a particular church
   in combination with any other module(s).
1. Underlying and supporting the _modules_,
   CC includes functionality we call **infrastructure**,
   which includes:
   
   1. Administrative functions (e.g., account creation)
   1. Authentication (using JSON Web Tokens)
   1. Role-based authorization 
   1. Internationalization (I18N) and Localization (L10N) 

1. Although we use the term **user** informally throughout,
   CC's data model does _not_ include a user entity.
   1. Any individual (human) tracked by the system we call a **Person**.
      The database includes a `Person` table.
   1.  

# Roles

This section details the roles implemented in CC.

## None

Portions of CC are available to completely unknown, unauthenticated users.
Strictly speaking, such a user does not have a role
and need not authenticate with CC.
However, for convenience, we consider such users to have a **public** "role"
that permits them access to _only_ the public content of the application.

_Example_: someone browsing a list of upcoming events 
or viewing the home church map to identify a home church.

## Infrastructure

1. An **administrative** (or **admin**) user is someone who can access 
   most of the "behind-the-scenes"
   administrative functions of the application across different modules.
   
   _Example_: church office worker adding a new account to the system
   or authorizing an existing account as having a particular role.
1. A **superuser** is a user with essentially unlimited access to CC.
   
   _Example_: info tech team member who wants to initialize portions of the database,
   upgrade CC to a new version, etc.
   
1. A **translator** is a user who can create or update localization
   (translation) data.
   
   _Example_: a user wants to localize CC into a previously unsupported 
   natural language. 

## Groups Module

1. A **group leader** is a user who is responsible for a _single_ group.

   _Example_: home church leader wants to add a new member to a
   home group or mark someone as having attended a meeting of the group. 
   
1. A **group overseer** is a user who has oversight over _multiple_
   groups.
   
   _Example_: user who wants to send a message to leaders of groups
   for which the overseer is responsible.

## Courses Module

1. A **registrar** is a user who manages the data in the `courses` module.

   _Example_: Christian education pastor who wants to create a new course
   or grant a diploma.

## Events Module

## Calendars Module
