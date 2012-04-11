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