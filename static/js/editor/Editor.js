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

Range = require('ace/range').Range;

cider.editor.Editor = function(config) {
    this.editor = null;
    this.mode = null;
    this.dirty = false;
    this.oldDirty = false;
    this.changeCallback = null;
    
    this.isDirty = function() {
        return this.dirty;
    };
    this.setDirty = function(value) {
        this.oldDirty = this.dirty;
        this.dirty = value;
    };
    this.revertDirty = function() {
        this.dirty = this.oldDirty;
    };
    
    this.getTabWidth = function() {
        return this.editor.getSession().getTabSize();
    };
    this.setTabWidth = function(width) {
        if(width !== '' && !isNaN(width)) {
            this.editor.getSession().setTabSize(parseInt(width));
        }
    };
    
    this.getMode = function() {
        return this.mode;
    };
    this.setMode = function(mode) {
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
                this.mode = mode;
                var Mode = require('ace/mode/' + mode).Mode;
                this.editor.getSession().setMode(new Mode());
                break;
        }
    };
    
    this.findNext = function() {
        this.editor.findNext();
    };
    
    this.findPrevious = function() {
        this.editor.findPrevious();
    };
    
    this.find = function(needle) {
        if(needle && needle !== '') {
            this.editor.find(needle);
        }
    };
    
    this.setReadOnly = function(value) {
        this.editor.setReadOnly(value);
    };
    
    this.initShortcuts = function(shortcuts) {
        var closure = this;
        
        if(typeof shortcuts.save != 'undefined') {
            this.editor.commands.addCommand({
                name : 'save',
                bindKey : {
                    win : 'Ctrl-S',
                    mac : 'Command-S'
                },
                exec : shortcuts.save
            });
        }
        
        if(typeof shortcuts.find != 'undefined') {
            this.editor.commands.addCommand({
                name : 'find',
                bindKey : {
                    win : 'Ctrl-F',
                    mac : 'Command-F'
                },
                exec : shortcuts.find
            });
            
            this.editor.commands.addCommand({
                name : 'findNext',
                bindKey : {
                    win : 'Ctrl-G',
                    mac : 'Command-G'
                },
                exec : function() { closure.findNext(); }
            });
            
            this.editor.commands.addCommand({
                name : 'findPrevious',
                bindKey : {
                    win : 'Ctrl-Shift-G',
                    mac : 'Command-Shift-G'
                },
                exec : function() { closure.findPrevious(); }
            });
        }
    };
    
    this.handleChange = function(e) {
        this.dirty = true;
        
        var diff = this.getDiff(e.data);
        
        if(this.changeCallback) {
            this.changeCallback(e, diff);
        }
    };
    
    this.getDiff = function(data) {
        var p = 0;
        var lines = this.editor.getSession().getDocument().getLines(
            0,
            data.range.start.row
        );
        for(var i = 0; i < lines.length; i++) {
            var line = lines[i];
            p += (i < data.range.start.row) ? line.length : data.range.start.column;
        }
        p += data.range.start.row;
        
        var diff = {
            p : p
        };
        switch(data.action) {
            case 'insertText':
                diff.i = data.text;
                diff.t = 'i';
                break;
            case 'insertLines':
                diff.i = data.lines.join('\n') + '\n';
                diff.t = 'i';
                break;
            case 'removeText':
                diff.d = data.text;
                diff.t = 'd';
                break;
            case 'removeLines':
                diff.d = data.lines.join('\n') + '\n';
                diff.t = 'd';
                break;
        }
        
        return diff;
    };
    
    this.executeDiff = function(diff) {
        var lines = this.editor.getSession().getDocument().getAllLines();
        switch(diff.t) {
            case 'd':
                var range = Range.fromPoints(
                    this.getOffset(diff.p, lines),
                    this.getOffset((diff.p + diff.d.length), lines)
                );
                this.editor.getSession().getDocument().remove(range);
                break;
            case 'i':
                this.editor.getSession().getDocument().insert(
                    this.getOffset(diff.p, lines),
                    diff.i
                );
                break;
        }
    };
    
    this.getOffset = function(offset, lines) {
        for(var row = 0; row < lines.length; row++) {
            var line = lines[row];
            if(offset <= line.length) {
                break;
            }
            offset -= lines[row].length + 1;
        }
        return {
            row : row,
            column : offset
        };
    };
    
    this.getText = function() {
        return this.editor.getSession().getValue();
    };
    
    this.init = function(config) {
        var closure = this;
        
        this.editor = ace.edit(config.editorId);
        this.setReadOnly(true);
        this.editor.setTheme('ace/theme/eclipse');
        this.editor.getSession().getDocument().setNewLineMode('unix');
        this.setTabWidth(config.tabWidth);
        this.editor.getSession().setUseSoftTabs(true);
        this.editor.getSession().setValue(
            this.editor.getSession().getValue().replace(
                /[~]lb/g,
                decodeURIComponent('%7B')
            ).replace(
                /[~]rb/g,
                decodeURIComponent('%7D')
            )
        );
        if(typeof config.mode != 'undefined') {
            this.setMode(config.mode);
        }
        
        if(typeof config.shortcuts != 'undefined') {
            this.initShortcuts(config.shortcuts);
        }
        
        if(typeof config.change != 'undefined') {
            this.changeCallback = config.change;
        }
        this.editor.getSession().on('change', function(e) {
            closure.handleChange(e);
        });
    };
    this.init(config);
};