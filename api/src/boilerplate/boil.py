#!/usr/bin/env python

"""
Output boilerplate code from configuration file.
"""

import json
import re
import sys

import yaml


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
    for attr in entity['attributes']:
        details = []

        if attr['type'] in ('integer', 'date', 'boolean'):
            details.append(attr['type'].capitalize())

        elif attr['type'] == 'string':
            details.append(model_string(attr))

        if attr.get('primary-key'):
            details.append('primary_key=True')

        fk = attr.get('foreign-key')
        if fk:
            details.append(f"ForeignKey('{fk}')")

        if attr.get('required'):
            details.append('nullable=False')

        if attr.get('unique'):
            details.append('unique=True')

        if attr.get('default'):
            details.append(f"default={attr['default']}")

        tab(f"{snake_case(attr['name'])} = Column({', '.join(details)})")

    if 'relationships' in entity:
        for rel in entity['relationships']:
            tab(f"{rel['name']} = relationship('{rel['related-model']}', backref='{rel['backref']}', lazy=True")


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

        if attr['type'] in ('integer', 'date', 'string', 'boolean'):
            type = attr['type'].capitalize()

        if attr.get('required'):
            required = True

        if attr.get('attribute'):
            details.append(f"attribute='{snake_case(attr['attribute'])}'")

        if attr.get('hide'):
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
    variable = entity['singular']
    print(f"""
@{module}.route('{entity["uri"]}', methods=['POST'])
@jwt_required
def create_{variable}():
    try:
        valid_{variable} = {variable}_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    new_{variable} = {variable}(**valid_{variable})
    db.session.add(new_{variable})
    db.session.commit()
    return jsonify({variable}_schema.dump(new_{variable})), 201
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


def generate_api(module, entity):
    print(f"# ---- {entity['name']}")
    print(f"{entity['singular']}_schema = {entity['name']}Schema()")
    generate_api_create(module, entity)
    generate_api_read_all(module, entity)
    generate_api_read_one(module, entity)
    generate_api_update(module, entity)


for file_name in sys.argv[1:]:
    spec = read_yaml(file_name)
    print(json.dumps(spec, indent=2))
    module = spec['module']
    banner(module, True)
    for entity in spec['entities']:
        banner('Model')
        generate_model(entity)
        banner('Schema')
        generate_schema(entity)
        banner('API')
        generate_api(module, entity)
