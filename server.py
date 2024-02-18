
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from tinydb import TinyDB, Query
from typing import List, Optional
import uuid

from threading import Lock

from secrets import token_hex

from fastapi.responses import HTMLResponse

from pydantic import BaseModel

app = FastAPI()


@app.post("/covert_to_gcode")
def list_notes(user: dict = Depends(get_user_by_api_key)):
    print(user)
    note_ids = user['note_ids']
    with main_lock:
        notes = [note_db.get(doc_id=note_id) for note_id in note_ids]
    return {"name": user['name'], "notes": [{'note_id': note.doc_id, 'title': note['title']} for note in notes if note]}


@app.get("/", response_class=FileResponse)
def read_root():
    return FileResponse("site.html")

app.mount("/", StaticFiles(directory="static"), name="static")


