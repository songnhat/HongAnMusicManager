from HongAnMusicManager_app.__init__ import db
from enum import Enum


class MusicWaveStatusSchema(Enum):
    WAIT = "wait"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


class MusicWave(db.Model):
    __tablename__ = "musicwave"

    id = db.Column(db.Integer, primary_key=True)
    file_mp3 = db.Column(db.String(200))
    file_background = db.Column(db.String(200))
    file_dance = db.Column(db.String(200))
    file_output = db.Column(db.String(200))
    gen_sin = db.Column(db.Boolean)
    time_created = db.Column(db.TIMESTAMP(timezone=True), server_default=db.func.now())
    status = db.Column(db.Enum(MusicWaveStatusSchema))
