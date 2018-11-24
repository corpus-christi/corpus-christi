# Corpus Christi

Corpus Christi (CC) is an an open-source, internationalized church management suite.

## Modules

- lead - admin
- gather - home church
- teach - training
- serve - ministry
- plan - calendaring

## Requirements

The package requires the following:

- Python 3.7 or later
- Node 10 LTS

## Development

Instructions for developing CC.

### Virtual environment

Use a virtual environment. Create:

    python3 -m venv venv

Activate (`bash`):

    source venv/bin/activate

### Required packages

Install the required Python packages.

    pip intall -r requirements.txt

### Vue
Compile and hot-reload for development
```
yarn run serve
```
Compile and minify for production
```
yarn run build
```
Run tests
```
yarn run test
```
Lint and fix files
```
yarn run lint
```

# Resources

Flask
- Flask Web Development, 2nd Edition, Miguel Grinberg, O'Reilly, 2018
- [Explore Flask](http://exploreflask.com/)

Vue
- [Vue](https://vuejs.org/)
- [Vue CLI](https://cli.vuejs.org/)

