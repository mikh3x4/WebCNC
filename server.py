
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
import tempfile

app = FastAPI()


@app.post("/convert_to_gocde/")
async def create_upload_file(input_file: UploadFile):
    # input_path = f"temp/{file.filename}"
    # with open(input_path, "wb") as buffer:
    #     buffer.write(await svg_file.read())

    scale_x = "5cm"
    scale_y = "5cm"

# vpype read /Users/mik/Downloads/Drawing\ 1-4.svg trim 1 1 linemerge --tolerance 0.1mm linesort scaleto 16cm 7cm layout  tight gwrite --profile my_own_plotter ~/test/test.gcode

    outfile = tempfile.SpooledTemporaryFile
    subprocess.run(["vpype", "read", "-",
                    "linemerge", "--tolerance", "0.1mm",
                    "linesort",
                    "scaleto", scale_x, scale_y,
                    "layout", "tight",
                    "gwrite", "--profile", "my_own_plotter", "-"],
               capture_output=True, stdin=input_file, stdout = outfile)

    return outfile
    # return outfile.read()
    # return {"filename": file.filename}

@app.get("/", response_class=FileResponse)
def read_root():
    return FileResponse("site.html")

app.mount("/", StaticFiles(directory="static"), name="static")


