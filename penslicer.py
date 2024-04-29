config='''
[gwrite.my_own_plotter]
unit = "mm"
document_start = "G90;\\nG10 P0 L20 X0 Y0 Z0;\\n"
layer_start = ""
line_start = ""
# segment_first = """G0 X{x:.4f} Y{y:.4f};
# M10 P0 S100;\\nG04 P500;\\n"""
segment_first = """G0 X{x:.4f} Y{y:.4f};
M10 P0 S100;\\n"""
segment = """G01 X{x:.4f} Y{y:.4f} F1000\\n"""
# line_end = """M10 P0 S30;\\nG04 P500;\\n"""
line_end = """M10 P0 S30;\\n"""
document_end = "M10 P0 S30\\nG0 X0 Y0"
invert_y = true
'''

with open("config.toml", "w") as f:
    f.write(config)

import asyncio
loop = asyncio.get_event_loop()

import time
text = None

from pyscript import when

import vpype_cli

import js
def handler(loop, context):
    js.console.error(context.message)
    print("hello")
    raise(context.exception)
loop.set_exception_handler(handler)

import traceback

# allows for javascript to access python variables
from js import createObject
from pyodide.ffi import create_proxy
createObject(create_proxy(globals()), "pyodideGlobals")

async def wrap(a):
    try:
        return await a
    except Exception as e:
        print("sad")
        print(e)
        print(traceback.format_exc())
        display(str(e), target="serialResults")
        display(traceback.format_exc(), target="serialResults")
    
from js import Uint8Array, File, URL, document
import io
from pyodide.ffi.wrappers import add_event_listener

gcode = None

def downloadFile(*args):
    data = gcode
    encoded_data = data.encode('utf-8')
    my_stream = io.BytesIO(encoded_data)

    js_array = Uint8Array.new(len(encoded_data))
    js_array.assign(my_stream.getbuffer())

    file = File.new([js_array], "unused_file_name.txt", {type: "text/plain"})
    url = URL.createObjectURL(file)

    hidden_link = document.createElement("a")
    hidden_link.setAttribute("download", "output.gcode")
    hidden_link.setAttribute("href", url)
    hidden_link.click()


async def process_file():
    global gcode
    display("sd", target="serialResults")
    file_input = Element("file-upload")
    uploaded_file = file_input.element.files.item(0)
    if uploaded_file is None:
        return

    file_name = uploaded_file.name

    print("2")
    file_type = file_name.split(".")[-1]

    if file_type == "gcode":
        gcode = await uploaded_file.text()
        with open("output.gcode", "w") as f:
            f.write(gcode)
        dest_elem = js.document.getElementById("output-image")
        dest_elem.innerHTML = gcode.replace("\n", "<br>")
        return

    print("1")

    if file_type == "jpeg":
        file_type = "jpg"

    assert file_type in ["png", "svg", "dxf", "jpg"]

    js_array = await uploaded_file.arrayBuffer()
    text = js_array.to_py().tobytes()
    input_cmd = "iread input.png "
    with open("input." + file_type, "wb") as f:
        f.write(text)

    input_cmd = {"png" : "iread input.png ",
                 "svg" : "read input.svg ",
                 "dxf" : "dread input.dxf ",
                 "jpg": "hatched --levels 64 128 192 -s 0.5 -p 4 input.jpg" }[file_type]

    # extra_pipeline = " trim 1 1 "

    print("hi")
    display("maigc", target="py-terminal")
    cmd = js.document.getElementById("vpype-pipline-config").value
    cmd = cmd.replace("{width}", js.document.getElementById("width_box").value)
    cmd = cmd.replace("{height}", js.document.getElementById("height_box").value)
    print("hi2")

    gcode_cmd = input_cmd + cmd + " gwrite --profile my_own_plotter output.gcode"
    preview_cmd = input_cmd + cmd + " write --pen-up output.svg"

    vpype_cli.execute(gcode_cmd, global_opt="-c config.toml")
    vpype_cli.execute(preview_cmd, global_opt="-c config.toml")

    with open("output.svg") as f:
        svg_as_string = f.read()

    with open("output.gcode") as f:
        gcode = f.read()

    dest_elem = js.document.getElementById("output-image")
    dest_elem.innerHTML = svg_as_string

    dest_elem.children[0].setAttribute("width", "auto")
    dest_elem.children[0].setAttribute("height", "auto")
    dest_elem.children[0].setAttribute("preserveAspectRatio", "xMidYMid meet")

