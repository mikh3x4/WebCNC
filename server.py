
from fastapi import FastAPI, HTTPException, Depends, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
# from tinydb import TinyDB, Query
from typing import List, Optional
import uuid

from threading import Lock

import uvicorn
# from secrets import token_hex

from fastapi.responses import HTMLResponse

from pydantic import BaseModel

import subprocess
import tempfile

app = FastAPI()


@app.post("/convert_to_gcode/")
async def create_upload_file(input_file: UploadFile):
    # input_path = f"temp/{file.filename}"
    # with open(input_path, "wb") as buffer:
    #     buffer.write(await svg_file.read())

    scale_x = "5cm"
    scale_y = "5cm"

# vpype read /Users/mik/Downloads/Drawing\ 1-4.svg trim 1 1 linemerge --tolerance 0.1mm linesort scaleto 16cm 7cm layout  tight gwrite --profile my_own_plotter ~/test/test.gcode
    content = await input_file.read()
    print(content)

    # outfile = tempfile.SpooledTemporaryFile()
    result = subprocess.run(["vpype", "--config", "vpype.toml", "read", "-",
                    "linemerge", "--tolerance", "0.1mm",
                    "linesort",
                    "scaleto", scale_x, scale_y,
                    "layout", "tight",
                    "gwrite", "--profile", "my_own_plotter", "-"],
                   input=content, capture_output=True)
    # gcode = outfile.read()

    svg_result = subprocess.run(["vpype", "--config", "vpype.toml", "read", "-",
                    "linemerge", "--tolerance", "0.1mm",
                    "linesort",
                    "scaleto", scale_x, scale_y,
                    "layout", "tight",
                    "write", "-"],
                   input=content, capture_output=True)

    gcode = result.stdout
    svg = svg_result.stdout

    print(gcode)

    return gcode
    # return outfile.read()
    # return {"filename": file.filename}

@app.get("/", response_class=FileResponse)
def read_root():
    return FileResponse("site.html")

@app.get("/convert", response_class=FileResponse)
def read_root():
    return FileResponse("convert.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# app.mount("/", StaticFiles(directory="static"), name="static")


