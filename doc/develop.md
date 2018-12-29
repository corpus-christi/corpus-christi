# Developing Corpus Christi

This document lays out the details 
of the development tools and environment
you will need to contribute to Corpus Christi (CC).

For more details on the development methodology
of the core team (including learning resources),
refer to `doc/sdm.md`.

## Requirements

The development tool chain requires the following software installed.
- [Python](https://www.python.org/) 3.7 or later
- [Node](https://nodejs.org/) 10 LTS or later
- [Yarn](https://yarnpkg.com/) current;
  could also use `npm`, but we assume Yarn.

## UI

The UI is based on [Vue](https://www.vuejs.com/)

### Install
Install node modules
```bash
yarn install
```

### Vue Commands
Compile and hot-reload for development
```bash
yarn run serve
```
Compile and minify for production
```bash
yarn run build
```
Run tests
```bash
yarn run test
```
Lint and fix files
```bash
yarn run lint
```

## API

The API is based on [Flask](http://flask.pocoo.org/).

### Virtual Environment

Use a virtual environment. Create:

    python3 -m venv venv

Activate (for `bash`):

    source venv/bin/activate

### Required packages

Install the required Python packages.

    pip install -r requirements.txt
