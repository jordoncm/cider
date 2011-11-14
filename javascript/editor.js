/**
 * This work is copyright Jordon Mears. All rights reserved. See license.txt 
 * for details.
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
};

window.onbeforeunload = function() {
    if(dirty) {
        return 'Document has unsaved changes; changes will be lost.';
    }
    
    if(saving) {
        return 'Save operation in progress; changes could be lost.';
    }
};

function save() {
    saving = true;
    document.getElementById('save').innerHTML = 'Saving...';
    oldDirty = dirty;
    dirty = false;
    var text = editor.getSession().getValue();
    new Ajax.Request(
        '../save-file/',
        {
            method : 'post',
            parameters : {
                file : file,
                text : text
            },
            onSuccess : function(transport) {
                var response = transport.responseText.evalJSON();
                
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
        }
    );
}