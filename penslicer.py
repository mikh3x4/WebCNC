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
    raise(context.exception)
loop.set_exception_handler(handler)


async def wrap(a):
    try:
        return await a
    except Exception as e:
        print(e)
    
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
    file_input = Element("file-upload")
    uploaded_file = file_input.element.files.item(0)
    if uploaded_file is None:
        return

    display("hi", target="serialResults")
    file_name = uploaded_file.name

    display("done", target="serialResults")

    width = 16
    height = 9

    if(file_name.split(".")[-1] == "png"):
        js_array = await uploaded_file.arrayBuffer()
        text = js_array.to_py().tobytes()
        input_cmd = "iread input.png"
        with open("input.png", "wb") as f:
            f.write(text)

    if(file_name.split(".")[-1] == "gcode"):
        gcode = await uploaded_file.text()
        with open("output.gcode", "w") as f:
            f.write(gcode)
        dest_elem = js.document.getElementById("output-image")
        dest_elem.innerHTML = gcode.replace("\n", "<br>")
        return

    if(file_name.split(".")[-1] == "svg"):
        text = await uploaded_file.text()
        input_cmd = "read input.svg"
        with open("input.svg", "w") as f:
            f.write(text)

    extra_pipeline = " trim 1 1 "
    extra_pipeline = ""

    command = input_cmd + extra_pipeline + f" linemerge --tolerance 0.1mm linesort scaleto {width}cm {height}cm layout tight "

    cmd = command + "gwrite --profile my_own_plotter output.gcode"
    print(cmd)

    vpype_cli.execute(cmd, global_opt="-c config.toml")
    vpype_cli.execute(command + "write --pen-up output.svg", global_opt="-c config.toml")

    with open("output.svg") as f:
        svg_as_string = f.read()

    with open("output.gcode") as f:
        gcode = f.read()

    dest_elem = js.document.getElementById("output-image")
    dest_elem.innerHTML = svg_as_string

    dest_elem.children[0].setAttribute("width", "auto")
    dest_elem.children[0].setAttribute("height", "auto")
    dest_elem.children[0].setAttribute("preserveAspectRatio", "xMidYMid meet")

