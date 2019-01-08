# ---- Event

class Event(Base):
     __tablename__ = 'events_event'
     id = Column(Integer, primary_key=True)
     title = Column(StringTypes.LONG_STRING, nullable=False)
     description = Column(StringTypes.LONG_STRING)
     start = Column(Datetime, nullable=False)
     end = Column(Datetime, nullable=False)
     location_id = Column(Integer, ForeignKey('places_location.id'))
     active = Column(Boolean, default=True)

        def __repr__(self):
            return f"<Event(id={self.id})>"
    

class EventSchema(Schema):
     id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
     title = fields.String(required=True, validate=Length(min=1))
     description = fields.String()
     start = fields.DateTime(required=True)
     end = fields.DateTime(required=True)
     location_id = fields.Integer(data_key='locationId')
     active = fields.Boolean()

# ---- Asset

class Asset(Base):
     __tablename__ = 'events_asset'
     id = Column(Integer, primary_key=True)
     description = Column(StringTypes.LONG_STRING, nullable=False)
     location_id = Column(Integer, ForeignKey('locations_location.location_id'))
     active = Column(Boolean, default=True)

        def __repr__(self):
            return f"<Asset(id={self.id})>"
    

class AssetSchema(Schema):
     id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
     description = fields.String(required=True)
     location_id = fields.Integer(data_key='locationId')
     active = fields.Boolean()

# ---- Team

class Team(Base):
     __tablename__ = 'events_teams'
     id = Column(Integer, primary_key=True)
     description = Column(StringTypes.LONG_STRING, nullable=False)
     active = Column(Boolean, default=True)

        def __repr__(self):
            return f"<Team(id={self.id})>"
    

class TeamSchema(Schema):
     id = fields.Integer(dump_only=True, required=True, validate=Range(min=1))
     description = fields.String(required=True)
     active = fields.Boolean()
