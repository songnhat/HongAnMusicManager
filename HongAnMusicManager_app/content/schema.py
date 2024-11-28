from marshmallow import Schema, fields
from .models import MusicWaveStatusSchema


class MusicWaveSchema(Schema):
    id = fields.Integer(dump_only=True)
    file_mp3 = fields.String()
    file_background = fields.String()
    file_dance = fields.String()
    file_output = fields.String()
    gen_sin = fields.Boolean()
    time_created = fields.DateTime("timestamp", dump_only=True)
    status = fields.Enum(MusicWaveStatusSchema)


class MusicWaveSearchSchema(Schema):
    id = fields.Integer()
    file_mp3 = fields.String()
    file_background = fields.String()
    file_dance = fields.String()
    file_output = fields.String()


class MusicWaveUpdateSchema(Schema):
    id = fields.Integer()
    file_mp3 = fields.String()
    file_background = fields.String()
    file_dance = fields.String()
    file_output = fields.String()
    gen_sin = fields.Boolean()
    status = fields.Enum(MusicWaveStatusSchema)


class MusicWaveDeleteSchema(Schema):
    id = fields.Integer()
