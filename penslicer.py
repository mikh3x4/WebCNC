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
    js.console.log("hello")
    js.console.error(context.message)
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
        print(e)
    
from js import Uint8Array, File, URL, document
import io
from pyodide.ffi.wrappers import add_event_listener

import re

gcode = None
gcode_bbox = None

from js import writer

def update_button_disabled_states():
    for el in js.document.querySelectorAll(".need_python"):
        el.disabled = False

    serial_avalible = writer is not None

    for el in js.document.querySelectorAll(".need_serial"):
        el.disabled = not serial_avalible

    gcode_avalible = gcode is not None

    for el in js.document.querySelectorAll(".need_file"):
        el.disabled = not gcode_avalible

    for el in js.document.querySelectorAll(".need_file_and_serial"):
        el.disabled = not (serial_avalible and gcode_avalible)

update_button_disabled_states()


def calculate_bbox():
    global gcode_bbox
    assert gcode != None

    # print(re.findall(r"X[0-9.]+[ ;\n]", gcode))
    # print(re.findall(r"Y[0-9.]+[ ;\n]", gcode))

    x_pos = [ float(m[1:-1]) for m in re.findall(r"X[0-9.]+[ ;\n]", gcode) ]
    y_pos = [ float(m[1:-1]) for m in re.findall(r"Y[0-9.]+[ ;\n]", gcode) ]

    min_x = min(x_pos)
    max_x = min(x_pos)

    gcode_bbox = "G90;\nG10 P0 L20 X0 Y0 Z0;\n" + \
            f"G0 X{min(x_pos):.4f} Y{min(y_pos):.4f};\n" + \
            f"G0 X{min(x_pos):.4f} Y{max(y_pos):.4f};\n" + \
            f"G0 X{max(x_pos):.4f} Y{max(y_pos):.4f};\n" + \
            f"G0 X{max(x_pos):.4f} Y{min(y_pos):.4f};\n" + \
            f"G0 X{min(x_pos):.4f} Y{min(y_pos):.4f};\n"

def downloadFile(*args):
    assert gcode != None

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

    file_input = Element("file-upload")
    uploaded_file = file_input.element.files.item(0)
    if uploaded_file is None:
        js.alert("Please select a file first")
        return

    js.document.querySelector(".loader").hidden = False
    asyncio.sleep(0.01)

    file_name = uploaded_file.name

    file_type = file_name.split(".")[-1]

    if file_type == "gcode":
        gcode = await uploaded_file.text()
        with open("output.gcode", "w") as f:
            f.write(gcode)
        dest_elem = js.document.getElementById("output-image")
        dest_elem.innerHTML = gcode.replace("\n", "<br>")
        calculate_bbox()
        return

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

    cmd = js.document.getElementById("vpype-pipline-config").value
    cmd = cmd.replace("{width}", js.document.getElementById("width_box").value)
    cmd = cmd.replace("{height}", js.document.getElementById("height_box").value)

    gcode_cmd = input_cmd + cmd + " gwrite --profile my_own_plotter output.gcode"
    preview_cmd = input_cmd + cmd + " write --pen-up output.svg"

    vpype_cli.execute(gcode_cmd, global_opt="-c config.toml")
    vpype_cli.execute(preview_cmd, global_opt="-c config.toml")

    with open("output.svg") as f:
        svg_as_string = f.read()

    with open("output.gcode") as f:
        gcode = f.read()

    calculate_bbox()

    dest_elem = js.document.getElementById("output-image")
    dest_elem.innerHTML = svg_as_string

    dest_elem.children[0].setAttribute("width", "auto")
    dest_elem.children[0].setAttribute("height", "auto")
    dest_elem.children[0].setAttribute("preserveAspectRatio", "xMidYMid meet")

    js.document.querySelector(".loader").hidden = True

