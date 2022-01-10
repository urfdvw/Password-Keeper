/**
 * Ace Related ***************************************************************************
 * https://ace.c9.io/demo/keyboard_shortcuts.html
 */


ace.require("ace/ext/language_tools");
var editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.session.setTabSize(4);
editor.session.setUseSoftTabs(true);
editor.session.setUseWrapMode(true);

editor.setOptions({
    maxLines: Infinity
});

// auto completion
// https://stackoverflow.com/a/19730470/7037749
editor.setOptions({
    enableBasicAutocompletion: true,
    enableLiveAutocompletion: true
});

editor.commands.addCommand({
    name: 'myCommand',
    bindKey: {win: 'Ctrl-S',  mac: 'Command-S'},
    exec: function(editor) {
        save_and_run(editor);
    },
});

editor.commands.addCommand({
    name: 'MyOutdent',
    bindKey: { win: 'Ctrl-[', mac: 'Cmd-[' },
    exec: function (editor) {
        console.log('MyOutdent')
        editor.blockOutdent();
    },
    multiSelectAction: "forEach",
    scrollIntoView: "selectionPart"
});

editor.commands.addCommand({
    name: 'MyIntdent',
    bindKey: { win: 'Ctrl-]', mac: 'Cmd-]' },
    exec: function (editor) {
        console.log('MyIntdent')
        editor.blockIndent();
    },
    multiSelectAction: "forEach",
    scrollIntoView: "selectionPart"
});

/**
 * File related functions *********************************************************
 */
let fileHandle;
var butOpenFile = document.getElementById("inputfile")
butOpenFile.addEventListener('click', async () => {
    [fileHandle] = await window.showOpenFilePicker();
    const file = await fileHandle.getFile();
    const contents = await file.text();
    editor.setValue(decode(contents), -1);
    document.getElementById('filename').innerHTML = fileHandle.name;
    document.title = fileHandle.name
});

async function writeFile(fileHandle, contents) {
    // Create a FileSystemWritableFileStream to write to.
    const writable = await fileHandle.createWritable();
    // Write the contents of the file to the stream.
    await writable.write(contents);
    // Close the file and write the contents to disk.
    await writable.close();
}

function save_and_run(editor) {
    writeFile(fileHandle, encode(editor.getValue()));
}

function download(data, filename, type) {
    // Function to download data to a file
    console.log(data)
    var file = new Blob([data], { type: type });
    if (window.navigator.msSaveOrOpenBlob) // IE10+
        window.navigator.msSaveOrOpenBlob(file, filename);
    else { // Others
        var a = document.createElement("a"),
            url = URL.createObjectURL(file);
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        setTimeout(function () {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }, 0);
    }
}

function save_code() {
    try {
        download(encode(editor.getValue()), fileHandle.name, 'text')
    } catch {
        download(encode(editor.getValue()), 'items.csv', 'text')
    }
}

function ascii_mod(n){
    var period = 126 - 32 + 1
    while (n > 126){
        n -= period;
    }
    while (n < 32){
        n += period;
    }
    return n
}

function chr(n) {
    return String.fromCharCode(n)
}

function ord(c){
    return c.charCodeAt(0);
}

function vigenere(plain, key, dir){
    var out = "";
    var i = 0;
    for (var j=0; j<plain.length; j++){
        out += chr(ascii_mod(ord(plain[j]) + ord(key[i]) * dir))
        i += 1
        if (i == key.length){
            i = 0;
        }
    }
    return out
}

function encode(plain) {
    return code(plain, -1)
}

function decode(plain) {
    return code(plain, 1)
}

function code(ciphered, dir) {
    var lines = ciphered.split('\n');
    for (var i=0; i<lines.length; i++){
        if (i==0){
            continue;
        }
        lines[i] = lines[i].trim().split(',')
        if (lines[i].length> 5){
            lines[i][4] = lines[i].slice(4, lines[i].length).join(',')
            lines[i] = lines[i].slice(0, 5)
            console.log(lines[i])
        }
        for (var j=0; j<lines[i].length; j++){
            lines[i][j] = lines[i][j].trim();
        }
        lines[i][lines[i].length - 1] = vigenere(
            lines[i][lines[i].length - 1], 
            document.getElementById('key').value, 
            dir
        )
        lines[i] = lines[i].join(',')
    }
    lines = lines.join('\n')
    return lines
}