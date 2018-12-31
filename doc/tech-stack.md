# Technology Stack

This document details the technology on which CC is implemented.
We consider the stack from "top to bottom."

Below each element of the stack are lists of learning resources,
including articles, books, and videos.
If you find additional helpful resources,
let us know!

## User interface (View)

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

## RESTful API Server (Controller)

1. [Flask](http://flask.pocoo.org/) - Python web microframework
    - [Flask Web Development](https://www.safaribooksonline.com/library/view/flask-web-development/9781491991725/) book
    - [Explore Flask](http://exploreflask.com/)
1. [Flask Mail](https://pythonhosted.org/Flask-Mail/) - Flask email framework
1. [Marshmallow](https://marshmallow.readthedocs.io/en/3.0/index.html) - API object serialization, deserialization, validation
1. [Flask JWT](https://flask-jwt-extended.readthedocs.io/en/latest/) - Client authentication
    - [JWT](https://jwt.io/) - All about JSON Web Tokens

## Data Persistence (Model)

1. [PostgreSQL](https://www.postgresql.org/) - Relational Database Management System
1. [SQL Alchemy](https://www.sqlalchemy.org/) - Python Object-Relational Mapper
    - [Object-Relational Tutorial](https://docs.sqlalchemy.org/en/latest/orm/tutorial.html)
    - [Essential SQLAlchemy](https://www.safaribooksonline.com/library/view/essential-sqlalchemy-2nd/9781491916544/) book
1. [Flask SQLAlchemy](http://flask-sqlalchemy.pocoo.org/) - Integration with [SQL Alchemy](https://www.sqlalchemy.org/)
1. [Alembic](https://alembic.sqlalchemy.org/) - Database migration for SQL Alchemy
    - [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
1. [Flask Migrate](https://flask-migrate.readthedocs.io) - Integration with [Alembic](https://alembic.sqlalchemy.org/)
    - [Main page]((https://flask-migrate.readthedocs.io)) explains the package well 

## Other Key Technologies

1. [JSON](http://json.org/) - Standard data interchange format
1. [YAML](https://yaml.org/) - Easy-to-read-and-write data format
   - [YAML Getting Started](https://yaml.org/start.html)
