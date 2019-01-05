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

1. `groups` - Home Church management and tracking
1. `courses` - Teaching ministry management
1. `events` - Event planning and registration
1. `calendar` - Planning and calendaring

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
