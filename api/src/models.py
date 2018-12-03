from . import db


class I18NLocale(db.Model):
    __tablename__ = 'i18n_locale'
    id = db.Column(db.String(16), primary_key=True)
    desc = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return "<I18NLocale {}>".format(self.desc)
