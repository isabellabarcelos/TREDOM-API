from marshmallow import Schema, fields, validate


class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()


class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)


class TagAndItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema)
    tag = fields.Nested(TagSchema)

class PatientSchema(Schema):
    name = fields.Str(required=True)
    birthday = fields.Date(required=True)
    location = fields.Str(required=True)
    gender = fields.Str(required=True)
    weight = fields.Decimal(required=True)
    race = fields.Str(required=True)
    height = fields.Decimal(required=True)

class HealthProfessionalSchema(Schema):
    name = fields.Str(required=True)
    birthday = fields.Date(required=True)
    location = fields.Str(required=True)
    gender = fields.Str(required=True)
    medical_register = fields.Str(required=True)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class UserRegisterSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    
class UserAndProfileSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    patient = fields.Nested(PatientSchema, allow_none=True)
    health_professional = fields.Nested(HealthProfessionalSchema, allow_none=True)