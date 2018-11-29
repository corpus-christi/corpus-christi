# Software Develoment Methodology

This document details the Software Develoment Methodology
that we use to build and maintain the Corpus Christi project
(abbreviated **CC** throughout).

## Matrix Organization

Initial develoment is matrixed along two dimensions:
_Features_ and _Functions_.

**Features**
are the top-level modules implemented in CC.
As of this writing, they are (with code names):

1. `lead` - Administration of the entire CC suite
1. `gather` - Home Church management and tracking
1. `teach` - Teaching ministry management
1. `serve` - Tracking for various ministries
1. `plan` - Planning and calendaring

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

### Pair programming

## Tool Chain

### Data persistence (Model)

1.  [PostgreSQL](https://www.postgresql.org/) (RDBMS)
2.  [SQL Alchemy](https://www.sqlalchemy.org/) (ORM)


### Application server (Controller)

1.  [Flask](http://flask.pocoo.org/)


### User interface (View)

1.  [Jinja](http://jinja.pocoo.org/docs/2.10/) (template engine)
2.  [Vue](https://vuejs.org/) (SPA framework)

### Testing


#### Unit

1.  [Python `unittest`](https://docs.python.org/3.7/library/unittest.html)
2.  [Pytest](https://docs.pytest.org/en/latest/contents.html#toc)
    -   Used by Mozilla and Dropbox over `unittest` or `nose`

#### End to End (E2E)

1.  [Cypress](https://www.cypress.io/)
    -   Shiny and new
    -   Selenium free - *yay*
    -   Dashboard service has an unlimited open-source plan
2.  [Nightwatch](http://nightwatchjs.org/)
    -   Selenium driven - *ick*


### Localization (I18N/L10N)

1.  [Python I18N](https://docs.python.org/3.7/library/gettext.html)

### Continuous Integration and Deployment (CI/CD)

#### Possible solutions

-   [Codeship](https://codeship.com/)
-   [Gitlab](https://about.gitlab.com/features/gitlab-ci-cd/)
-   [CircleCI](https://circleci.com/)
-   [Jenkins](https://jenkins.io/)
-   [Travis](https://travis-ci.org/)


#### [Linode](https://www.linode.com/)

-   [CI/CD](https://www.linode.com/docs/development/ci/introduction-ci-cd/)
-   [Automated CI/CD with Jenkins](https://www.linode.com/docs/development/ci/automate-builds-with-jenkins-on-ubuntu/)

#### Tools

-   [Ansible](https://www.ansible.com/)

## Daily Schedule

Unless otherwise announced,
this will be our work day schedule.

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-right" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-right">Time</th>
<th scope="col" class="org-left">Activity</th>
<th scope="col" class="org-left">Notes</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-right">8:30</td>
<td class="org-left">Devotions</td>
<td class="org-left">Church staff, team members</td>
</tr>


<tr>
<td class="org-right">9:00</td>
<td class="org-left">Stand-up</td>
<td class="org-left">Module teams</td>
</tr>


<tr>
<td class="org-right">9:15</td>
<td class="org-left">Work</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-right">12:00</td>
<td class="org-left">Lunch</td>
<td class="org-left">Catered in at Arco</td>
</tr>


<tr>
<td class="org-right">1:00</td>
<td class="org-left">Stand-up</td>
<td class="org-left">Functional teams, Team leads</td>
</tr>


<tr>
<td class="org-right">1:15</td>
<td class="org-left">Work</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-right">3:15</td>
<td class="org-left">Afternoon break</td>
<td class="org-left">Snackies</td>
</tr>


<tr>
<td class="org-right">3:30</td>
<td class="org-left">Work</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-right">5:00</td>
<td class="org-left">End of work day</td>
<td class="org-left">&#xa0;</td>
</tr>
</tbody>
</table>

## Other Issues

### TODO Revision Control

-   Git branching models
    -   [Workflow descriptions at Atlassian](https://www.atlassian.com/git/tutorials/comparing-workflows)
    -   [Gitflow (Dreissen@nvie)](https://nvie.com/posts/a-successful-git-branching-model/)
    -   [Github Flow](https://guides.github.com/introduction/flow/)

### TODO Progress tracking (Trello? Zenhub? Other?)

### TODO Support requests (Trello? Something else?)

### TODO Slack utilization?

### TODO Seating arrangement for best team interaction

### TODO Ask about increasing Internet bandwidth

-   Offer to pay overage during January

### TODO Ask about WiFi

-   Offer to buy more WAPs if necessary

