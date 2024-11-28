from flask import Blueprint, json, request
from HongAnMusicManager_app.content import models, schema
from HongAnMusicManager_app.content.models import db
from webargs.flaskparser import use_args
import logging

api_bp = Blueprint("music_wave", __name__)

logger = logging.getLogger(__name__)


@api_bp.route("/music_wave/add", methods=["POST"])
def add():
    try:
        json_data = request.get_json(force=True)
        items = schema.MusicWaveSchema().load(json_data)
        _file_mp3 = items["file_mp3"]
        _file_background = items["file_background"]
        _file_dance = items["file_dance"]
        _file_output = items["file_output"]
        _gen_sin = items["gen_sin"]
        _status = items["status"]
        try:
            new_music_wave = models.MusicWave(
                file_mp3=_file_mp3,
                file_background=_file_background,
                file_dance=_file_dance,
                file_output=_file_output,
                gen_sin=_gen_sin,
                status=_status,
            )
            db.session.add(new_music_wave)
            db.session.commit()
            return schema.MusicWaveSchema().dumps(new_music_wave)
        except Exception as e:
            db.session.rollback()
            logger.critical(e, exc_info=True)
            return json.dumps({"error": str(e)})
    except Exception as e:
        logger.critical(e, exc_info=True)
        return json.dumps({"error": str(e)})


@api_bp.route("/music_wave/update", methods=["POST"])
def update():
    try:
        session = db.session
        json_data = request.get_json(force=True)
        items = schema.MusicWaveUpdateSchema().load(json_data)
        id = items["id"]
        query = session.query(models.MusicWave)
        query = query.filter(models.MusicWave.id == id)
        query.update(
            {
                "file_mp3": items["file_mp3"],
                "file_background": items["file_background"],
                "file_dance": items["file_dance"],
                "file_output": items["file_output"],
                "gen_sin": items["gen_sin"],
                "status": items["status"],
            }
        )
        db.session.commit()
        result = (
            session.query(models.MusicWave)
            .filter(models.MusicWave.id == id)
            .one_or_none()
        )
        return schema.MusicWaveSchema().dumps(result)
    except Exception as e:
        db.session.rollback()
        logger.critical(e, exc_info=True)
        return json.dumps({"error": str(e)})


@api_bp.route("/music_wave/delete", methods=["DELETE"])
@use_args(schema.MusicWaveDeleteSchema, location="query")
def delete(args):
    try:
        session = db.session
        id = args["id"]
        query = session.query(models.MusicWave).filter(models.MusicWave.id == id)
        if query.one_or_none():
            query = query.delete()
            db.session.commit()
            return schema.MusicWaveSchema().dumps(query)
        else:
            return json.dumps({"error": "Not found"})
    except Exception as e:
        logger.critical("Cannot delete music wave")
        return json.dumps({"error": str(e)})


@api_bp.route("/music_wave/search", methods=["GET"])
@use_args(schema.MusicWaveSearchSchema, location="query")
def get(args):
    try:
        session = db.session
        query = session.query(models.MusicWave)
        if args.get("id"):
            id = args["id"]
            query = query.filter(models.MusicWave.id == id)
        if args.get("file_mp3"):
            file_mp3 = args["file_mp3"]
            query = query.filter(models.MusicWave.file_mp3.like(f"%{file_mp3}%"))
        if args.get("file_background"):
            file_background = args["file_background"]
            query = query.filter(
                models.MusicWave.file_background.like(f"%{file_background}%")
            )
        if args.get("file_dance"):
            file_dance = args["file_dance"]
            query = query.filter(models.MusicWave.file_dance.like(f"%{file_dance}%"))
        if args.get("file_output"):
            file_output = args["file_output"]
            query = query.filter(models.MusicWave.file_output.like(f"%{file_output}%"))
        result = query.all()

        return schema.MusicWaveSchema().dumps(result, many=True)
    except Exception as e:
        logger.critical(e, exc_info=True)
        return json.dumps({"error": str(e)})
