# Software Develoment Methodology

This document details the Software Develoment Methodology
that we use to build and maintain the Corpus Christi project
(abbreviated **CC** throughout).

## Matrix Organization

Initial develoment is matrixed along two dimensions:
_Features_ and _Functions_.

### Features

**Features**
are the top-level modules implemented in CC.
As of this writing, they are (with code names):

1. `lead` - Administration of the entire CC suite
1. `gather` - Home Church management and tracking
1. `teach` - Teaching ministry management
1. `serve` - Tracking for various ministries
1. `plan` - Planning and calendaring

### Functions

**Functions**
refers to the technology or management
elements that collectively implement **features**.
They are:

1.  Data persistence (Model)
1.  User interface (View)
1.  Application server (Controller)
1.  Testing (Unit and E2E)
1.  Localization (I18N/L10N)
1.  Dev Ops (CI/CD)

### Teams and Leadership

A team forms around a **feature**
and is responsible for building that feature.
A **feature owner** leads a feature team.
He or she takes responsibility for the overall completion
of the feature, ensuring that it meets customer requirements.

Each team member
has a particular **functional focus**
(e.g., UI, testing, or dev ops).
*All* functions must be covered within a team.

A designated **functional expert**
for each function
supports team members having the
corresponding functional focus.
The functional expert works _across_ different feature team.

### Pair programming

We use **pair programming**
to develop all production code.
Every line of code is overseen
by two developers working in tandem.
Our goals are to have built-in quality review during develoment
and to encourage developers to have greater courage
in moving their feature forward.

### Stand Up Meetings

Most days we hold two [stand-up meetings](https://en.wikipedia.org/wiki/Stand-up_meeting):
1. A *Feature Stand-Up* includes
   all members of a feature team,
   and is led by the feature owner.
   The purpose of this meeting
   is to communicate infomration
   about the feature itself.
1.  A *Function Stand-Up* includes
   members from across feature teams
   that have the same functional focus
   (e.g., all those working on data persistence).
   The purpose of this meeting
   is to cross-pollinate information
   on each layer of the tech stack
   across functional teams.

## Technology Stack

This section details the technology on which CC is implemented.
We consider the stack from "top to bottom."

Below each element of the stack are lists of learning resources,
including articles, books, and videos.
If you find additional helpful resources,
let us know!

### User interface (View)

CC is a single-page application (SPA).
Implemented with the following technologies.

1. [Vue](https://vuejs.org/) - progressive JavaScript framework
    - [View Tutorial](https://youtu.be/78tNYZUS-ps) video
    - [Get Started](https://vuejs.org/v2/guide/) guide
    - [Vue.js Up & Running](https://www.safaribooksonline.com/library/view/vuejs-up-and/9781491997239/) book
    - [List of Vue tutorials](https://madewithvuejs.com/tutorials)
1. [Vue Router](https://router.vuejs.org/) - client-side router
    - [Get Started](https://router.vuejs.org/guide/) guide
1. [Vuex](https://vuex.vuejs.org/) - state management
    - [Video Introduction](https://vuex.vuejs.org/) on main page
1. [Vuetify](https://vuetifyjs.com/en/) - Material Design component framework
1. [VueI18n](https://kazupon.github.io/vue-i18n/) - internationalization

### RESTful API Server (Controller)

1. [Flask](http://flask.pocoo.org/) - Python web microframework
    - [Flask Web Development](https://www.safaribooksonline.com/library/view/flask-web-development/9781491991725/) book
    - [Explore Flask](http://exploreflask.com/)
1. [Flask Mail](https://pythonhosted.org/Flask-Mail/) - Flask email framework
1. [Flask SQLAlchemy](http://flask-sqlalchemy.pocoo.org/) - Integration with [SQL Alchemy](https://www.sqlalchemy.org/)
    - [Main page](http://flask-sqlalchemy.pocoo.org/) has good documentation
    - [Quickstart](http://flask-sqlalchemy.pocoo.org/2.3/quickstart/) guide for basics
1. [Flask Migrate](https://flask-migrate.readthedocs.io) - Integration with [Alembic](https://alembic.sqlalchemy.org/)
    - [Main page]((https://flask-migrate.readthedocs.io)) explains the package well 

### Data Persistence (Model)

1. [PostgreSQL](https://www.postgresql.org/) - Relational Database Management System
1. [SQL Alchemy](https://www.sqlalchemy.org/) - Python Object-Relational Mapper
    - [Object-Relational Tutorial](https://docs.sqlalchemy.org/en/latest/orm/tutorial.html)
    - [Essential SQLAlchemy](https://www.safaribooksonline.com/library/view/essential-sqlalchemy-2nd/9781491916544/) book
1. [Alembic](https://alembic.sqlalchemy.org/) - Database migration for SQL Alchemy
    - [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

### Other Key Technologies

1. [JSON](http://json.org/) - Standard data interchange format
1. [JWT](https://jwt.io/) - JavaScript Web Tokens

## Tool Chain

The following tools are in common use in CC development

### General

1. [Venv](https://docs.python.org/3/library/venv.html) - Python virtual environment
1. [Vue CLI](https://cli.vuejs.org/) - Tooling for Vue development
1. [Vue development tools](https://github.com/vuejs/vue-devtools) - Browser plugin for Vue

### Revision Control

1. [Git](https://git-scm.com/) - distributed revision control
    - [Pro Git Book](https://git-scm.com/book/en/v2) - free on-line
    - [Getting Git Right](https://www.atlassian.com/git) - tutorial
    - [Git Cheatsheet](https://ndpsoftware.com/git-cheatsheet.html) - nifty interactive visual cheat sheet
    - [Git Learning Lab](https://lab.github.com/)
    - [Learn Git Branching](https://learngitbranching.js.org/) - interactive tutorial
    - [Learning Resources](https://try.github.io/) for Git
1. [GitHub](https://github.com) - Git hosting
    - [Learning Resources](https://try.github.io/) for GitHub

### Testing

#### User Interface

1. [Vue Test Utils](https://vue-test-utils.vuejs.org/) - Vue-specific test utilities
1. [Jest](https://jestjs.io/en/) - Test runner
1. [Mocha](https://mochajs.org/) - Test framework
1. [Chai](https://www.chaijs.com/) - Assertion library
1. [Sinon](https://sinonjs.org/) - Spies, stubs, and mocks for JavaScript

#### RESTful API

1. [Postman](https://www.getpostman.com/) - API test tool
1. [Pytest](https://docs.pytest.org/en/latest/contents.html#toc) - Python testing

#### End-to-End

1. [Cypress](https://www.cypress.io/) - Cool new testing environment

### Dev Ops

1. [Linode](https://www.linode.com/) - Hosting provider
1. [Circle CI](https://circleci.com/) - Continuous integration and deployment
1. [Ansible](https://www.ansible.com/) - Automation

### Development Environment

1. [PyCharm](https://www.jetbrains.com/pycharm/)
1. [Visual Studio Code](https://code.visualstudio.com/)

## Daily Schedule

- 08:30	Devotions (Church staff, team members)
- 09:00	Stand-up (Feature teams)
- 09:15	Work	 
- 12:00	Lunch
- 13:00	Stand-up (Functional teams)
- 13:15	Work	 
- 15:15	Break
- 15:30	Work	 
- 17:00	End of work day	 

## Process

### User Stories

We add capability to CC by implementing **user stories**
from the customer.
A user story is *not* a complete specification,
but is, instead, a reminder to have a conversation
with the feature owner about exactly how the system
should behave when the story is implemented.

### Tracking

We will track the process of implementing user stories
using [ZenHub](https://app.zenhub.com/).
ZenHub is an online project tracking tool 
similar to [Trello](https://trello.com/),
but integrated with GitHub.
It tracks tasks and progress
using GitHub's standard _issue_
feature, thus keeping all project
updates with the repository itself.

### Git

The project will use 
a Git branching model based on
[Gitflow](https://nvie.com/posts/a-successful-git-branching-model/)
and
[Github Flow](https://guides.github.com/introduction/flow/).

We use
[pull requests](https://help.github.com/categories/collaborating-with-issues-and-pull-requests/)
on GitHub to submit updates to release branches.
Pull requests are approved by feature owners.
