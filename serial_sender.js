
var port, textEncoder, writableStreamClosed, writer, historyIndex = -1;
var recv_buffer = [];
var estop_var = false;

// allwos for sharing code with python
// https://jeff.glass/post/pyscript-js-functions-original/
function createObject(x, variableName){
let execString = variableName + " = x"
console.log("Running `" + execString + "`");
eval(variableName + " = x")
}

const lineHistory = [];
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function rungcode(python_var_name) {
console.log("running gcode");

	var content = pyodideGlobals.get(python_var_name)

	    if (content == null){
		    alert("No gcode loaded")
		    return;
	    }

	   if ( writer == null){
		   alert("No plotter connected")
		    return;
	   }

	 var lines = content.split(/\r\n|\n/);

	isWaitingForOk = true;

	//for (let line of lines) {
	for (let i = 0; i < lines.length; i++) {
	    let line = lines[i]; // Get the current line using index

	    while(true){
		console.log("sending", line);
		recv_buffer = "";
		await sendData(line);

		console.log("sent");
		while (!recv_buffer.includes("ok") && !recv_buffer.includes("error")) {
		    await sleep(10); // Short sleep to prevent blocking
		    if(estop_var){
			break;
		    }
		}
		
		if(recv_buffer.includes("ok")){
		    console.log("got ok");
		    break;
		}
		console.log("resending");
		await sleep(50);

		if(estop_var){
		    break;
		}

	    }

	    console.log(line);

	    if(estop_var){
		break;
	    }
	}
	console.log("STOPPED")

	isWaitingForOk = false;

}



async function connectSerial() {
try {
    // Prompt user to select any serial port.
    port = await navigator.serial.requestPort();
    await port.open({ baudRate: 115200 });
    let settings = {};

    if (localStorage.dtrOn == "true") settings.dataTerminalReady = true;
    if (localStorage.rtsOn == "true") settings.requestToSend = true;
    if (Object.keys(settings).length > 0) await port.setSignals(settings);

    
    textEncoder = new TextEncoderStream();
    writableStreamClosed = textEncoder.readable.pipeTo(port.writable);
    writer = textEncoder.writable.getWriter();
    await listenToPort();
} catch (e){
    alert("Serial Connection Failed" + e);
}
}
async function sendCharacterNumber() {
document.getElementById("lineToSend").value = String.fromCharCode(document.getElementById("lineToSend").value);
}
async function sendSerialLine() {
dataToSend = document.getElementById("lineToSend").value;
lineHistory.unshift(dataToSend);
historyIndex = -1; // No history entry selected

dataToSend = dataToSend + "\n";

if (document.getElementById("echoOn").checked == true) appendToTerminal("> " + dataToSend);
await writer.write(dataToSend);
if (dataToSend.trim().startsWith('\x03')) echo(false);
document.getElementById("lineToSend").value = "";
document.getElementById("lineToSend").value = "";
}
var commandQueue = [];
var isWaitingForOk = false;

async function sendData(dataToSend) {

dataToSend = dataToSend + "\n";

if (document.getElementById("echoOn").checked == true) appendToTerminal("> " + dataToSend);
await writer.write(dataToSend);
}

async function NEWsendData(dataToSend) {
// Add commands to the queue instead of sending them directly
console.log("sending", isWaitingForOk);
commandQueue.push(dataToSend + "\n");
processQueue();
}

async function processQueue() {
console.log("processing queue");
console.log("waiting for ok", isWaitingForOk);
// If we're already processing the queue or it's empty, do nothing
if (isWaitingForOk || commandQueue.length === 0) {
    return;
}

console.log("next command ");
// Send the next command in the queue
const dataToSend = commandQueue.shift();
if (document.getElementById("echoOn").checked == true) appendToTerminal("> " + dataToSend);
await writer.write(dataToSend);
isWaitingForOk = true; // Set flag to wait for "ok"
}



async function listenToPort() {
const textDecoder = new TextDecoderStream();
const readableStreamClosed = port.readable.pipeTo(textDecoder.writable);
const reader = textDecoder.readable.getReader();

// Listen to data coming from the serial device.
while (true) {

	const { value, done } = await reader.read();
	if (done) {
	    // Allow the serial port to be closed later.
	    console.log('[readLoop] DONE', done);
	    reader.releaseLock();
	    break;
	}
	appendToTerminal(value);
	recv_buffer += value;
}
}

async function NEWlistenToPort() {
const textDecoder = new TextDecoderStream();
port.readable.pipeTo(textDecoder.writable);
const reader = textDecoder.readable.getReader();
while (true) {
    const { value, done } = await reader.read();
    if (done) {
	console.log('[readLoop] DONE', done);
	reader.releaseLock();
	break;
    }
    console.log("got value");
    console.log(value);
    // Check for "ok" response

    appendToTerminal(value);
     //var lines = value.split(/\r\n|\n/);
    //lines.forEach(function(line) {
	//console.log("got line", line);
	//if ( value.includes("ok")) {
	    //console.log("processing next line");
	    //isWaitingForOk = false; // Ready to send the next command
	    //processQueue(); // Try processing the next command in the queue
	//}
    //});

    console.log("got ok");
    isWaitingForOk = false; // Ready to send the next command
    processQueue(); // Try processing the next command in the queue
}
}

const serialResultsDiv = document.getElementById("serialResults");
async function appendToTerminal(newStuff) {
serialResultsDiv.innerHTML += newStuff;
if (serialResultsDiv.innerHTML.length > 3000) serialResultsDiv.innerHTML = serialResultsDiv.innerHTML.slice(serialResultsDiv.innerHTML.length - 3000);

//scroll down to bottom of div
serialResultsDiv.scrollTop = serialResultsDiv.scrollHeight;
}
function scrollHistory(direction) {
// Clamp the value between -1 and history length
historyIndex = Math.max(Math.min(historyIndex + direction, lineHistory.length - 1), -1);
if (historyIndex >= 0) {
    document.getElementById("lineToSend").value = lineHistory[historyIndex];
} else {
    document.getElementById("lineToSend").value = "";
}
}
document.getElementById("lineToSend").addEventListener("keyup", async function (event) {
if (event.keyCode === 13) {
    sendSerialLine();
} else if (event.keyCode === 38) { // Key up
    scrollHistory(1);
} else if (event.keyCode === 40) { // Key down
    scrollHistory(-1);
}
})
document.getElementById("echoOn").checked = (localStorage.echoOn == "false" ? false : true);

