#!/usr/bin/env python3

"""
Output boilerplate code from configuration file.
"""

import json
import re
import sys

import yaml
from jsonschema import validate, ValidationError


def read_yaml(file_name):
    data = None
    with open(file_name, "r") as f:
        data = yaml.load(f)
    return data


def kebab_case(s):
    return s.lower().replace('-', '_')


def snake_case(s):
    return s.lower().replace('-', '_')


def camel_case(s):
    words = re.split('[^A-Za-z0-9]', s)
    first = words[0].lower()
    rest = [word.capitalize() for word in words[1:]]
    return "".join([first] + rest)


def tab(string, n=1):
    print(" " * n * 4, string)


def rule(n, char='='):
    return char * n;


def banner(string, fat=False):
    string = f"{rule(10)} {string} {rule(10)}"
    if fat:
        r = rule(len(string))
        print("\n".join(['', r, string, r, '']))
    else:
        print("\n" + string + "\n")


def comment(s):
    print(f"\n# ---- {s}\n")


def model_string(attr):
    type_map = {'short': 'SHORT_STRING',
                'medium': 'MEDIUM_STRING',
                'long': 'LONG_STRING',
                'i18n': 'I18N_KEY',
                'locale': 'LOCALE_CODE',
                'password': 'PASSWORD_HASH'}

    length = attr.get('length')
    if length is None:
        raise RuntimeError(f"String type for {json.dumps(attr, indent=4)} must have a 'length' value")
    if length in type_map:
        return f"StringTypes.{type_map[length]}"
    return f"String({length})"


def generate_model(entity):
    print(f"class {entity['name']}(Base):")
    tab(f"__tablename__ = '{entity['table']}'")

    primary_keys = []
    for attr in entity['attributes']:
        details = []

        if attr['type'] in ('integer', 'date', 'boolean', 'datetime', 'float'):
            details.append(attr['type'].capitalize())
        elif attr['type'] == 'string':
            details.append(model_string(attr))
        else:
            raise ValidationError(f"Unknown type: {attr['type']}")

        fk = attr.get('foreign-key')
        if fk:
            details.append(f"ForeignKey('{fk}')")

        if attr.get('primary-key'):
            details.append('primary_key=True')
            primary_keys.append(attr['name'])

        if attr.get('required'):
            details.append('nullable=False')

        if attr.get('unique'):
            details.append('unique=True')

        if attr.get('default'):
            details.append(f"default={attr['default']}")

        tab(f"{snake_case(attr['name'])} = Column({', '.join(details)})")

    if 'relationships' in entity:
        for rel in entity['relationships']:
            tab(f"{rel['name']} = relationship('{rel['related-model']}', backref='{rel['backref']}', lazy=True)")

    repr_fields = [f"{pk}={{self.{pk}}}" for pk in primary_keys]
    print(f"""
        def __repr__(self):
            return f"<{entity['name']}({','.join(repr_fields)})>"
    """)


def generate_schema(entity):
    print(f"class {entity['name']}Schema(Schema):")
    for attr in entity['attributes']:
        details = []
        type = None
        required = False
        validators = []

        if attr.get('primary-key'):
            details.append('dump_only=True')
            required = True

        if '_' in attr['name'] or '-' in attr['name']:
            details.append(f"data_key='{camel_case(attr['name'])}'")

        if attr['type'] in ('integer', 'date', 'string', 'boolean', 'float'):
            type = attr['type'].capitalize()
        elif attr['type'] == 'datetime':
            type = 'DateTime'
        else:
            raise ValidationError(f"Unknown type: {attr['type']}")

        if attr.get('required'):
            required = True

        if attr.get('model-attribute'):
            details.append(f"attribute='{snake_case(attr['model-attribute'])}'")

        if attr.get('private'):
            details.append("load_only=True")

        if attr.get('min'):
            validators.append(f"Range(min={attr['min']})")

        if attr.get('min-length'):
            validators.append(f"Length(min={attr['min-length']})")

        if attr.get('one-of'):
            quoted_values = [f"'{val}'" for val in attr['one-of']]
            validators.append(f"OneOf([{', '.join(quoted_values)}])")

        if required:
            details.append('required=True')

        if len(validators) == 1:
            details.append(f"validate={validators[0]}")
        elif len(validators) > 1:
            details.append(f"validate=[{', '.join(validators)}]")

        tab(f"{snake_case(attr['name'])} = fields.{type}({', '.join(details)})")


def generate_api_create(module, entity):
    name, singular = entity['name'], entity['singular']
    print(f"""
@{module}.route('{entity["uri"]}', methods=['POST'])
@jwt_required
def create_{singular}():
    try:
        valid_{singular} = {singular}_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_{singular} = {name}(**valid_{singular})
    db.session.add(new_{singular})
    db.session.commit()
    return jsonify({singular}_schema.dump(new_{singular})), 201
    """)


def generate_api_read_all(module, entity):
    print(f"""
@{module}.route('{entity["uri"]}')
@jwt_required
def read_all_{entity['plural']}():
    result = db.session.query({entity['name']}).all()
    return jsonify({entity['singular']}_schema.dump(result, many=True))
    """)


def generate_api_read_one(module, entity):
    name, singular, plural = entity['name'], entity['singular'], entity['plural']
    print(f"""
@{module}.route('{entity["uri"]}/<{singular}_id>')
@jwt_required
def read_one_{singular}({singular}_id):
    result = db.session.query({name}).filter_by(id={singular}_id).first()
    return jsonify({singular}_schema.dump(result))
    """)


def generate_api_replace(module, entity):
    name, uri, singular, plural = entity['name'], entity['uri'], entity['singular'], entity['plural']
    print(f"""
@{module}.route('{uri}/<{singular}_id>', methods=['PUT'])
@jwt_required
def replace_{singular}({singular}_id):
    pass
    """)


def generate_api_update(module, entity):
    name, uri, singular, plural = entity['name'], entity['uri'], entity['singular'], entity['plural']
    print(f"""
@{module}.route('{uri}/<{singular}_id>', methods=['PATCH'])
@jwt_required
def update_{singular}({singular}_id):
    try:
        valid_{singular} = {singular}_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    {singular} = db.session.query({name}).filter_by(id={singular}_id).first()

    for key, val in valid_{singular}.items():
        setattr({singular}, key, val)

    db.session.commit()
    return jsonify({singular}_schema.dump({singular}))
    """)


def generate_api_delete(module, entity):
    name, uri, singular, plural = entity['name'], entity['uri'], entity['singular'], entity['plural']
    print(f"""
@{module}.route('{uri}/<{singular}_id>', methods=['DELETE'])
@jwt_required
def delete_{singular}({singular}_id):
    pass
    """)


def generate_api(module, entity):
    print(f"{entity['singular']}_schema = {entity['name']}Schema()")
    generate_api_create(module, entity)
    generate_api_read_all(module, entity)
    generate_api_read_one(module, entity)
    generate_api_replace(module, entity)
    generate_api_update(module, entity)
    generate_api_delete(module, entity)


def generate_test(name):
    print(f"""
@pytest.mark.xfail()
def test_{name}(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
    """)


def generate_tests(entity):
    singular, plural = entity['singular'], entity['plural']
    generate_test(f"create_{singular}")
    generate_test(f"read_all_{plural}")
    generate_test(f"read_one_{singular}")
    generate_test(f"replace_{singular}")
    generate_test(f"update_{singular}")
    generate_test(f"delete_{singular}")


schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "CC Boilerplate",
    "type": "object",
    "properties": {
        "module": {
            "description": "Name of the CC module (e.g., `people`, `groups`)",
            "type": "string"
        },
        "entities": {
            "description": "Details of each entity (in the ERD sense)",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "description": "Name of this entity, capitalized",
                        "type": "string"
                    },
                    "singular": {
                        "description": "Lower-case singular form of the entity name",
                        "type": "string"
                    },
                    "plural": {
                        "description": "Lower-case plural form of the entity name",
                        "type": "string"
                    },
                    "uri": {
                        "description": "Partial URI of endpoints for this entity (e.g., `/accounts`)",
                        "type": "string"
                    },
                    "table": {
                        "description": "Database table name for this entity (e.g., `people_person`)",
                        "type": "string"
                    },
                    "attributes": {
                        "description": "All attributes for this entity",
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "description": "Name of this attribute",
                                    "type": "string"
                                },
                                "type": {
                                    "description": "Type of this attribute",
                                    "type": "string"
                                },
                                "primary-key": {
                                    "description": "Whether this attribute is part of the primary key",
                                    "type": "boolean"
                                },
                                "min": {
                                    "description": "Minimum allowed value (numeric types only)",
                                    "type": "number"
                                },
                                "min-length": {
                                    "description": "Minimum length for this attribute (string types only)",
                                    "type": "integer"
                                },
                                "required": {
                                    "description": "Whether this attribute is required",
                                    "type": "boolean"
                                },
                                "default": {
                                    "description": "Default value for this attribute",
                                    "oneOf": [
                                        {"type": "string"},
                                        {"type": "number"},
                                        {"type": "boolean"}
                                    ]
                                },
                                "unique": {
                                    "description": "Whether this attribute must have a unique value for all instances",
                                    "type": "boolean"
                                },
                                "private": {
                                    "description": "Whether this attribute should remain server-side only",
                                    "type": "boolean"
                                },
                                "model-attribute": {
                                    "description": "Model attribute to which this schema field maps",
                                    "type": "string"
                                },
                                "length": {
                                    "description": "Length (string types only)",
                                    "oneOf": [
                                        {
                                            "type": "integer"
                                        },
                                        {
                                            "enum": [
                                                "short", "medium", "long",
                                                "i18n", "locale", "password"
                                            ]
                                        }
                                    ]
                                },
                                "one-of": {
                                    "description": "List of valid values for this attributee",
                                    "type": "array",
                                    "items": {
                                        "description": "One of the valid values",
                                        "type": "string"
                                    }
                                },
                                "foreign-key": {
                                    "description": "The `table.column` referenced by this foreign key field",
                                    "type": "string",
                                    "pattern": "^\w+\.\w+"
                                }
                            },
                            "required": ["name", "type"],
                            "additionalProperties": False
                        }

                    },
                    "relationships": {
                        "description": "Relationships in which this entity participates",
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "description": "Relationship name",
                                    "type": "string"
                                },
                                "related-model": {
                                    "description": "Entity at the other end of the relationship (SQLA Model)",
                                    "type": "string"
                                },
                                "backref": {
                                    "description": "Name by which the other end refers to this one",
                                    "type": "string"
                                }
                            },
                            "required": ["name", "related-model", "backref"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["name", "singular", "plural", "uri", "table", "attributes"],
                "additionalProperties": False
            }
        }
    },
    "required": ["module", "entities"],
    "additionalProperties": False
}

for file_name in sys.argv[1:]:
    spec = read_yaml(file_name)
    if False:
        # Output the raw spec.
        print(json.dumps(spec, indent=2))

    try:
        validate(spec, schema)
    except ValidationError as err:
        print("Validation failed", err)
        exit(1)

    module = spec['module']
    entities = spec['entities']

    banner("Models and Schemata", True)
    for entity in entities:
        comment(entity['name'])
        generate_model(entity)
        print()
        generate_schema(entity)

    banner("APIs", True)
    for entity in entities:
        comment(entity['name'])
        generate_api(module, entity)

    banner("Tests", True)
    for entity in entities:
        comment(entity['name'])
        generate_tests(entity)
