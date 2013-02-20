/*
 * This work is copyright 2011 - 2013 Jordon Mears. All rights reserved.
 *
 * This file is part of Cider.
 *
 * Cider is free software: you can redistribute it and/or modify it under the
 * terms of the GNU General Public License as published by the Free Software
 * Foundation, either version 3 of the License, or (at your option) any later
 * version.
 *
 * Cider is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
 * details.
 *
 * You should have received a copy of the GNU General Public License along with
 * Cider. If not, see <http://www.gnu.org/licenses/>.
 */

cider.namespace('cider.views.editor');

cider.views.editor.Menu = cider.views.View.extend({
    events: {
        'click #permalink-btn': 'showPermalink',
        'click #settings-btn': 'showSettings',
        'click #save': 'save'
    },
    template: _.template(cider.templates.editor.MENU),
    contextSchema: ['save_text', 'save_class', 'file', 'extra', 'read_only'],
    contextDefaults: {
        save_text: 'Save',
        save_class: 'btn-warning',
        file: '',
        extra: '',
        read_only: false
    },
    initialize: function() {
        this.subscribe('//editor/change', _.bind(this.editorDirty, this));
        this.subscribe('//editor/saving', _.bind(this.saving, this));
        this.subscribe('//editor/clean', _.bind(this.editorClean, this));
        this.subscribe('//editor/dirty', _.bind(this.editorDirty, this));
        this.subscribe('//socket/message/n', _.bind(this.updateEditors, this));
        this.subscribe('//socket/message/s', _.bind(this.editorClean, this));
    },
    editorClean: function() {
        $('#save').removeClass('btn-warning');
        $('#save').addClass('btn-success');
        $('#save').html('Saved');
    },
    editorDirty: function() {
        $('#save').removeClass('btn-success');
        $('#save').addClass('btn-warning');
        $('#save').html('Save');
    },
    updateEditors: function(data) {
        $('#editors-title').html(data.n.length + ' editors');
        $('#editors-list li').remove();
        for(var j = 0; j < data.n.length; j++) {
            $('#editors-list').append(
                '<li><a>' + data.n[j] + '</a></li>'
            );
        }
    },
    save: function() {
        if(!this.options.read_only) {
            this.publish('//editor/save');
        }
    },
    saving: function() {
        $('#save').html('Saving...');
    },
    showPermalink: function() {
        this.publish('//permalink/show');
    },
    showSettings: function() {
        this.publish('//settings/show');
    }
});

cider.views.editor.Editor = cider.views.View.extend({
    template: _.template(cider.templates.editor.EDITOR),
    contextSchema: ['text'],
    contextDefaults: {text: ''},
    socketSuppress: false,
    dirty: false,
    oldDirty: false,
    editor: null,
    mode: null,
    initialize: function() {
        this.subscribe('//preferences/stw', _.bind(this.updateTabWidth, this));
        this.subscribe(
            '//preferences/stwm',
            _.bind(this.updateTabWidthMarkup, this)
        );
        this.subscribe(
            '//preferences/' + this.options.highlight_mode_key,
            _.bind(this.setMode, this)
        );
        this.subscribe('//editor/save', _.bind(this.prepareSave, this));
        this.subscribe('//file/saved', _.bind(this.handleSaved, this));
        this.subscribe('//socket/open', _.bind(function() {
            if(!this.options.read_only) {
                this.setReadOnly(false);
            }
        }, this));
        this.subscribe('//socket/message/d', _.bind(this.executeDiff, this));
        this.subscribe('//socket/message/i', _.bind(this.executeDiff, this));
        this.subscribe('//socket/message/s', _.bind(function() {
            this.setDirty(false);
        }, this));
        this.subscribe('//editor/find', _.bind(this.find, this));
        this.subscribe(
            '//editor/find/previous',
            _.bind(this.findPrevious, this)
        );
        this.subscribe('//editor/find/next', _.bind(this.findNext, this));
        this.subscribe(
            '//editor/current/line',
            _.bind(this.emitCurrentLine, this)
        );
    },
    /**
     * Renders the editor.
     *
     * Must be called explicitly outside of the render function as the
     * container div must be attached to the DOM before the editor can be
     * rendered.
     */
    renderEditor: function() {
        this.editor = this.editor = ace.edit('editor');
        this.setReadOnly(true);
        this.editor.setTheme('ace/theme/eclipse');
        this.editor.getSession().getDocument().setNewLineMode('unix');
        this.setTabWidth(this.options.tab_width);
        this.editor.getSession().setUseSoftTabs(true);
        this.editor.getSession().setValue(
            this.editor.getSession().getValue().replace(
                /[&]lt;/g,
                '<'
            ).replace(
                /[&]gt;/g,
                '>'
            ).replace(
                /[&]amp;/g,
                '&'
            )
        );
        if(this.options.mode) {
            this.setMode(this.options.mode);
        }
        // NOTE: Editor does not seem to be "ready" right away and will set the
        // cursor position, but not scroll. Added hack of a timeout to work
        // around this.
        window.setTimeout(_.bind(function() {
            this.editor.gotoLine(parseInt(cider.argument('l', 0)));
        }, this), 250);

        this.editor.commands.addCommand({
            name: 'save',
            bindKey: {win: 'Ctrl-S', mac: 'Command-S'},
            exec: function() {
                cider.events.publish('//editor/save');
            }
        });

        this.editor.commands.addCommand({
            name: 'find',
            bindKey: {win: 'Ctrl-F', mac: 'Command-F'},
            exec: function() {
                cider.events.publish('//search');
            }
        });

        this.editor.commands.addCommand({
            name: 'findNext',
            bindKey: {win: 'Ctrl-G', mac: 'Command-G'},
            exec: function() {
                cider.events.publish('//editor/find/next');
            }
        });

        this.editor.commands.addCommand({
            name: 'findPrevious',
            bindKey: {win: 'Ctrl-Shift-G', mac: 'Command-Shift-G'},
            exec: function() {
                cider.events.publish('//editor/find/previous');
            }
        });

        this.editor.getSession().on('change', _.bind(this.handleChange, this));
    },
    setDirty: function(value) {
        this.oldDirty = this.dirty;
        this.dirty = value;
    },
    revertDirty: function() {
        this.dirty = this.oldDirty;
    },
    setTabWidth: function(width) {
        if(width !== '' && !isNaN(width)) {
            this.editor.getSession().setTabSize(parseInt(width));
        }
    },
    updateTabWidth: function(value) {
        if(this.mode.markup === undefined || !this.mode.markup) {
            this.setTabWidth(value);
        }
    },
    updateTabWidthMarkup: function() {
        if(this.mode.markup !== undefined && this.mode.markup) {
            this.setTabWidth(value);
        }
    },
    setReadOnly: function(value) {
        this.editor.setReadOnly(value);
    },
    setMode: function(mode) {
        for(var i = 0; i < this.options.modes.length; i++) {
            if(this.options.modes[i][1].mode == mode) {
                this.mode = this.options.modes[i][1];
                var Mode = ace.require('ace/mode/' + mode).Mode;
                this.editor.getSession().setMode(new Mode());
                if(this.mode.markup !== undefined && this.mode.markup) {
                    this.setTabWidth(cider.Preferences.get('stwm', 2));
                } else {
                    this.setTabWidth(cider.Preferences.get('stw', 4));
                }
                break;
            }
        }
    },
    isDirty: function() {
        return this.dirty;
    },
    handleChange: function(e) {
        this.dirty = true;
        var diff = this.getDiff(e.data);
        this.publish('//editor/change', diff);
        if(!this.socketSuppress) {
            this.publish('//socket/send', diff);
        }
    },
    prepareSave: function() {
        if(!this.options.read_only) {
            if(cider.Preferences.get('sttws')) {
                this.trimLines();
            }
            if(cider.Preferences.get('ssn')) {
                this.trimToSingleNewline();
            }
            this.setDirty(false);
            this.publish('//editor/saving');
            this.publish('//file/save', this.getText());
        }
    },
    handleSaved: function(response) {
        if(!response.success) {
            if(!this.isDirty()) {
                this.revertDirty();
            }
        }
        if(!this.isDirty()) {
            this.publish('//editor/clean');
        } else {
            this.publish('//editor/dirty');
        }
    },
    getCurrentLine: function() {
        return this.editor.getSelectionRange().start.row + 1;
    },
    emitCurrentLine: function() {
        this.publish('//editor/current/line/response', this.getCurrentLine());
    },
    getText: function() {
        return this.editor.getSession().getValue();
    },
    getDiff: function(data) {
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
            p: p
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
    },
    executeDiff: function(diff) {
        this.socketSuppress = true;
        Range = ace.require('ace/range').Range;
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
        this.socketSuppress = false;
    },
    getOffset: function(offset, lines) {
        for(var row = 0; row < lines.length; row++) {
            var line = lines[row];
            if(offset <= line.length) {
                break;
            }
            offset -= lines[row].length + 1;
        }
        return {
            row: row,
            column: offset
        };
    },
    focus: function() {
        this.editor.focus();
    },
    trimLines: function() {
        Range = ace.require('ace/range').Range;
        var lines = this.editor.getSession().getDocument().getAllLines();
        var pos = -1;
        for(var i = 0; i < lines.length; i++) {
            var line = lines[i];
            if((pos = line.search(/ +$/i)) != -1) {
                var range = Range.fromPoints(
                    {row: i, column: pos},
                    {row: i, column: line.length}
                );
                this.editor.getSession().getDocument().remove(range);
            }
        }
    },
    trimToSingleNewline: function() {
        var lines = this.editor.getSession().getDocument().getAllLines();
        if(lines[lines.length - 1].search(/^ *$/i) == -1) {
            this.editor.getSession().getDocument().insert(
                {row: lines.length - 1, column: lines[lines.length - 1].length},
                '\n'
            );
        } else if(!(lines[lines.length - 1] === '' && lines[lines.length - 2].search(/^ *$/i) == -1)) {
            var last = -1;
            for(var i = lines.length - 1; i >= 0; i--) {
                var line = lines[i];
                if(line.search(/^ *$/i) == -1) {
                    last = i;
                    break;
                }
            }

            if(last > -1) {
                this.editor.getSession().getDocument().removeLines(
                    last + 1,
                    lines.length - 1
                );
                this.editor.getSession().getDocument().insert(
                    {row: last, column: lines[last].length},
                    '\n'
                );
            }
        }
    },
    find: function(needle) {
        if(needle && needle !== '') {
            this.editor.find(needle);
        }
    },
    findPrevious: function() {
        this.editor.findPrevious();
    },
    findNext: function() {
        this.editor.findNext();
    }
});

cider.views.editor.FindBar = cider.views.View.extend({
    events: {
        'click #find-previous-btn': 'findPrevious',
        'click #find-next-btn': 'findNext',
        'keyup #find': 'find'
    },
    template: _.template(cider.templates.editor.FIND_BAR),
    initialize: function() {
        this.subscribe('//search', _.bind(this.search, this));
    },
    search: function() {
        var element = $('#find');
        element.select();
        this.find();
    },
    find: function() {
        var element = $('#find');
        if(element.val() !== '') {
            this.publish('//editor/find', element.val());
        }
    },
    findPrevious: function() {
        this.publish('//editor/find/previous');
    },
    findNext: function() {
        this.publish('//editor/find/next');
    }
});

cider.views.editor.Permalink = cider.views.View.extend({
    template: _.template(cider.templates.editor.PERMALINK),
    contextSchema: ['url'],
    contextDefaults: {url: ''},
    initialize: function() {
        this.subscribe(
            '//permalink/show',
            _.bind(this.askForCurrentLine, this)
        );
        this.subscribe(
            '//editor/current/line/response',
            _.bind(this.showPermalink, this)
        );
    },
    askForCurrentLine: function() {
        this.publish('//editor/current/line');
    },
    showPermalink: function(line) {
        var url = window.location.href.replace(/\?l=[0-9]*/, '?').replace(/\&l=[0-9]*/, '') + '&l=' + line;
        $('#permalink-link').html(url);
        $('#permalink-link').attr('href', url);
        $('#permalink').modal('show');
    }
});

cider.views.editor.Settings = cider.views.View.extend({
    events: {
        'change #stw': 'handleIntSetting',
        'change #stwm': 'handleIntSetting',
        'change #shm': 'handleModeSetting',
        'change #sttws': 'handleBooleanSetting',
        'change #ssn': 'handleBooleanSetting'
    },
    template: _.template(cider.templates.editor.SETTINGS),
    contextSchema: ['mode', 'modes'],
    contextDefaults: {mode: 'text'},
    initialize: function() {
        this.subscribe('//settings/show', _.bind(this.showSettings, this));
    },
    render: function() {
        var context = this.getContext();
        context.stw = cider.Preferences.get('stw', 4);
        context.stwm = cider.Preferences.get('stwm', 2);
        context.sttws = cider.Preferences.get('sttws', false);
        context.ssn = cider.Preferences.get('ssn', false);
        this.$el.html(this.template(context));
        return this;
    },
    handleBooleanSetting: function(e) {
        cider.Preferences.set(
            $(e.target).attr('id'),
            $(e.target).is(':checked')
        );
    },
    handleIntSetting: function(e) {
        cider.Preferences.set(
            $(e.target).attr('id'),
            parseInt($(e.target).val())
        );
    },
    handleModeSetting: function(e) {
        cider.Preferences.set(
            this.options.highlight_mode_key,
            $(e.target).val()
        );
    },
    showSettings: function() {
        $('#settings').modal('show');
    }
});
