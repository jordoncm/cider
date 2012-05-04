/**
 * This work is copyright 2011 Jordon Mears. All rights reserved.
 * 
 * This file is part of Cider.
 * 
 * Cider is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * Cider is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with Cider.  If not, see <http://www.gnu.org/licenses/>.
 */

var editor = null;
var dirty = false;
var oldDirty = false;
var saving = false;

window.onload = function() {
    editor = ace.edit('editor');
    editor.setTheme('ace/theme/eclipse');
    if(typeof mode != 'undefined') {
        var Mode = require('ace/mode/' + mode).Mode;
        editor.getSession().setMode(new Mode());
    }
    editor.getSession().setTabSize(tabWidth);
    editor.getSession().setUseSoftTabs(true);
    editor.getSession().setValue(
        editor.getSession().getValue().replace(
            /[~]lb/g,
            decodeURIComponent('%7B')
        ).replace(
            /[~]rb/g,
            decodeURIComponent('%7D')
        )
    );
    
    editor.getSession().on('change', function() {
        document.getElementById('save').innerHTML = 'Save';
        dirty = true;
    });
    
    editor.commands.addCommand({
        name : 'save',
        bindKey : {
            win : 'Ctrl-S',
            mac : 'Command-S',
            sender : 'editor'
        },
        exec : save
    });
    
    editor.commands.addCommand({
        name : 'find',
        bindKey : {
            win : 'Ctrl-F',
            mac : 'Command-F',
            sender : 'editor'
        },
        exec : find
    });
    
    editor.commands.addCommand({
        name : 'findNext',
        bindKey : {
            win : 'Ctrl-G',
            mac : 'Command-G',
            sender : 'editor'
        },
        exec : findNext
    });
    
    editor.commands.addCommand({
        name : 'findPrevious',
        bindKey : {
            win : 'Ctrl-Shift-G',
            mac : 'Command-Shift-G',
            sender : 'editor'
        },
        exec : findPrevious
    });
};

window.onbeforeunload = function() {
    if(dirty) {
        return 'Document has unsaved changes; changes will be lost.';
    }
    
    if(saving) {
        return 'Save operation in progress; changes could be lost.';
    }
};

window.onkeydown = function(e) {
    if(e.ctrlKey || e.metaKey) {
        switch(e.keyCode) {
            case 'F'.charCodeAt(0):
                e.preventDefault();
                find();
                break;
            case 'G'.charCodeAt(0):
                e.preventDefault();
                if(e.shiftKey) {
                    findPrevious();
                } else {
                    findNext();
                }
                break;
            case 'S'.charCodeAt(0):
                e.preventDefault();
                save();
                break;
        }
    }
}

function save() {
    saving = true;
    document.getElementById('save').innerHTML = 'Saving...';
    oldDirty = dirty;
    dirty = false;
    var text = editor.getSession().getValue();
    $.ajax({
        url : '../save-file/',
        type : 'POST',
        dataType : 'json',
        data : {
            file : file,
            text : text
        },
        success : function(response) {
            if(!response.success) {
                if(!dirty) {
                    dirty = oldDirty;
                }
            }
            
            if(!dirty) {
                document.getElementById('save').innerHTML = 'Saved';
            } else {
                document.getElementById('save').innerHTML = 'Save';
            }
            
            saving = false;
        }
    });
}

function setTabWidth(width) {
    if(width !== '' && !isNaN(width)) {
        editor.getSession().setTabSize(parseInt(width));
    }
}

function setHighlightMode(mode) {
    switch(mode) {
        case 'c_cpp':
        case 'clojure':
        case 'coffee':
        case 'coldfusion':
        case 'csharp':
        case 'css':
        case 'golang':
        case 'groovy':
        case 'haxe':
        case 'html':
        case 'java':
        case 'javascript':
        case 'json':
        case 'latex':
        case 'less':
        case 'liquid':
        case 'lua':
        case 'markdown':
        case 'ocaml':
        case 'perl':
        case 'pgsql':
        case 'php':
        case 'powershell':
        case 'python':
        case 'ruby':
        case 'scad':
        case 'scala':
        case 'scss':
        case 'sh':
        case 'sql':
        case 'svg':
        case 'text':
        case 'textile':
        case 'xml':
        case 'xquery':
            var Mode = require('ace/mode/' + mode).Mode;
            editor.getSession().setMode(new Mode());
            break;
    }
}

function find() {
    var element = document.getElementById('find');
    element.select();
    if(element.value !== '') {
        search(element.value);
    }
}

function findNext() {
    editor.findNext();
}

function findPrevious() {
    editor.findPrevious();
}

function search(needle) {
    if(needle && needle !== '') {
        editor.find(needle);
    }
}