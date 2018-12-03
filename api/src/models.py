from . import db


class I18NLocale(db.Model):
    __tablename__ = 'i18n_locale'
    id = db.Column(db.String(16), primary_key=True)
    desc = db.Column(db.String(64), unique=True, nullable=False)
    values = db.relationship('I18NValue', backref='locale', lazy=True)

    def to_json(self):
        return {
            'id': self.id,
            'desc': self.desc
        }

    def __repr__(self):
        return "<I18NLocale {}>".format(self.desc)


class I18NKey(db.Model):
    __tablename__ = 'i18n_key'
    id = db.Column(db.String(128), primary_key=True)
    desc = db.Column(db.String(256), unique=True, nullable=False)
    values = db.relationship('I18NValue', backref='key', lazy=True)

    def __repr__(self):
        return "<I18NKey {}>".format(self.id)


class I18NValue(db.Model):
    __tablename__ = 'i18n_value'
    key_id = db.Column(db.String(128), db.ForeignKey('i18n_key.id'), primary_key=True)
    locale_id = db.Column(db.String(16), db.ForeignKey('i18n_locale.id'), primary_key=True)
    gloss = db.Column(db.Text(), nullable=False)

    def __repr__(self):
        return "<I18NValue {} {}>".format(self.key_id, self.locale_id)
