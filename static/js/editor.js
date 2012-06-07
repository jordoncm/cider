/**
 * This work is copyright 2012 Jordon Mears. All rights reserved.
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

cider.namespace('cider.editor');

cider.editor.save = function() {
    $('#save').html('Saving...');
    editorObj.setDirty(false);
    fileObj.save(editorObj.getText());
};

cider.editor.saveCallback = function(response) {
    if(!response.success) {
        if(!editorObj.isDirty()) {
            editorObj.revertDirty();
        }
    }
    
    if(!editorObj.isDirty()) {
        $('#save').html('Saved');
    } else {
        $('#save').html('Save');
    }
};

cider.editor.makeSaved = function() {
    editorObj.setDirty(false);
    $('#save').html('Saved');
};

cider.editor.setTabWidth = function(width) {
    editorObj.setTabWidth(width);
};

cider.editor.setHighlightMode = function(mode) {
    editorObj.setMode(mode);
};

cider.editor.find = function() {
    var element = $('#find');
    element.select();
    if(element.val() !== '') {
        search(element.val());
    }
};

cider.editor.findNext = function() {
    editorObj.findNext();
};

cider.editor.findPrevious = function() {
    editorObj.findPrevious();
};

cider.editor.search = function(needle) {
    if(needle && needle !== '') {
        editorObj.find(needle);
    }
    
    return false;
};

cider.editor.initTabWidth = function() {
    var tmp = preferencesObj.get('stw');
    if(tmp) {
        $('#stw').val(preferencesObj.get('stw'));
        if(!markup) {
            cider.editor.setTabWidth(parseInt(tmp));
        }
    }
    tmp = preferencesObj.get('stwm');
    if(tmp) {
        $('#stwm').val(preferencesObj.get('stwm'));
        if(markup) {
            cider.editor.setTabWidth(parseInt(tmp));
        }
    }
};

cider.editor.saveTabWidth = function(type, width) {
    if(markup && type == 'stwm') {
        cider.editor.setTabWidth(width);
    }
    if(!markup && type == 'stw') {
        cider.editor.setTabWidth(width);
    }
    preferencesObj.set(type, width);
};

cider.editor.generateId = function() {
    var text = '';
    var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for(var i = 0; i < 5; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
};

var editorObj = null;
var fileObj = null;
var socketObj = null;
var preferencesObj = null;

$(function() {
    var editorSettings = {
        editorId : 'editor',
        tabWidth : tabWidth,
        shortcuts : {
            save : cider.editor.save,
            find : cider.editor.find
        },
        change : function(e, diff) {
            $('#save').html('Save');
            socketObj.send(diff);
        }
    };
    if(typeof mode != 'undefined') {
        editorSettings.mode = mode;
    }
    editorObj = new cider.editor.Editor(editorSettings);
    
    fileObj = new cider.editor.File({
        file : file,
        saveCallback : cider.editor.saveCallback
    });
    
    preferencesObj = new cider.Preferences();
    
    cider.editor.initTabWidth();
    
    try {
        socketObj = new cider.editor.Socket({
            openCallback : function() {
                var kvp = location.search.substr(1).split('&');
                var args = {};
                for(var i = 0; i < kvp.length; i++) {
                    try {
                        var tmp = kvp[i].split('=');
                        args[tmp[0]] = tmp[1];
                    } catch(e) {}
                }
                var name = preferencesObj.get('sname');
                if(!name) {
                    name = 'cider-' + cider.editor.generateId();
                }
                socketObj.send({t : 'f', f : args.file, v : -1, n : name});
                editorObj.setReadOnly(false);
            },
            messageCallback : function(m) {
                console.log(m.data);
                var dataList = JSON.parse(m.data);
                for(var i = 0; i < dataList.length; i++) {
                    var data = dataList[i];
                    socketObj.suppress = true;
                    switch(data.t) {
                        case 'd':
                        case 'i':
                            editorObj.executeDiff(data);
                            break;
                        case 's':
                            cider.editor.makeSaved();
                            break;
                        case 'n':
                            $('#editorsTitle').html(data.n.length + ' editors');
                            $('#editorsList li').remove();
                            for(var j = 0; j < data.n.length; j++) {
                                $('#editorsList').append(
                                    '<li><a>' + data.n[j] + '</a></li>'
                                );
                            }
                            break;
                    }
                    socketObj.suppress = false;
                }
            }
        });
    } catch(e) {
        editorObj.setReadOnly(false);
        console.log(e);
    }
});

window.onbeforeunload = function() {
    /* $(window).unload does not appear to be consistent. */
    if(editorObj.isDirty()) {
        return 'Document has unsaved changes; changes will be lost.';
    }
    
    if(fileObj.isSaving()) {
        return 'Save operation in progress; changes could be lost.';
    }
};

$(window).keydown(function(e) {
    if(e.ctrlKey || e.metaKey) {
        switch(e.keyCode) {
            case 'F'.charCodeAt(0):
                e.preventDefault();
                cider.editor.find();
                break;
            case 'G'.charCodeAt(0):
                e.preventDefault();
                if(e.shiftKey) {
                    cider.editor.findPrevious();
                } else {
                    cider.editor.findNext();
                }
                break;
            case 'S'.charCodeAt(0):
                e.preventDefault();
                cider.editor.save();
                break;
        }
    }
});