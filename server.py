
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

import subprocess

app = FastAPI()


@app.post("/covert_to_gcode")
def list_notes(user: dict = Depends(get_user_by_api_key)):
    print(user)
    note_ids = user['note_ids']
    with main_lock:
        notes = [note_db.get(doc_id=note_id) for note_id in note_ids]
    return {"name": user['name'], "notes": [{'note_id': note.doc_id, 'title': note['title']} for note in notes if note]}

@app.post("/convert_to_gocde/")
async def create_upload_file(file: UploadFile):
    # Save the uploaded SVG file temporarily
    input_path = f"temp/{file.filename}"
    with open(input_path, "wb") as buffer:
        buffer.write(await svg_file.read())

    scale_x
    scale_y

# vpype read /Users/mik/Downloads/Drawing\ 1-4.svg trim 1 1 linemerge --tolerance 0.1mm linesort scaleto 16cm 7cm layout  tight gwrite --profile my_own_plotter ~/test/test.gcode
    subprocess.run(["vpype", "read", input_file,
                    "linemerge", "--tolerance", "0.1mm",
                    "linesort",
                    "scaleto", scale_x, scale_y,
                    "layout", "tight",
                    "gwrite", "--profile", "my_own_plotter", outfile],
                   capture_output=True)


    return {"filename": file.filename}

@app.get("/", response_class=FileResponse)
def read_root():
    return FileResponse("site.html")

app.mount("/", StaticFiles(directory="static"), name="static")


