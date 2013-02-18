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

cider.views.editor.Menu = Backbone.View.extend({
    events: {
        'click #settings-btn': 'showSettings',
        'click #save': 'save'
    },
    template: _.template(cider.templates.editor.MENU),
    initialize: function() {
        cider.events.on(
            '//editor/change',
            _.bind(this.handleEditorChange, this)
        );
        cider.events.on('//editor/clean', _.bind(this.editorClean, this));
        cider.events.on('//editor/dirty', _.bind(this.editorDirty, this));
        cider.events.on('//socket/message/n', _.bind(this.updateEditors, this));
        cider.events.on('//socket/message/s', _.bind(this.editorClean, this));
    },
    render: function() {
        var context = _.pick(
            this.options || {},
            ['save_text', 'save_class', 'file', 'extra']
        );
        context = _.defaults(context, {
            save_text: 'Save',
            save_class: 'btn-warning',
            file: '',
            extra: ''
        });
        this.$el.html(this.template(context));
        return this;
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
    handleEditorChange: function() {
        this.editorDirty();
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
        $('#save').html('Saving...');
        cider.events.trigger('//editor/save');
    },
    showSettings: function() {
        cider.events.trigger('//settings/show');
    }
});

cider.views.editor.Editor = Backbone.View.extend({
    template: _.template(cider.templates.editor.EDITOR),
    socketSuppress: false,
    dirty: false,
    oldDirty: false,
    editor: null,
    mode: null,
    preferences: null,
    initialize: function() {
        this.preferences = new cider.Preferences();
        cider.events.on('//preferences/stw', _.bind(this.updateTabWidth, this));
        cider.events.on(
            '//preferences/stwm',
            _.bind(this.updateTabWidthMarkup, this)
        );
        cider.events.on(
            '//preferences/' + this.options.highlight_mode_key,
            _.bind(this.setMode, this)
        );
        cider.events.on('//editor/save', _.bind(this.prepareSave, this));
        cider.events.on('//file/saved', _.bind(this.handleSaved, this));
        cider.events.on('//socket/open', _.bind(function() {
            this.setReadOnly(false);
        }, this));
        cider.events.on('//socket/message/d', _.bind(this.executeDiff, this));
        cider.events.on('//socket/message/i', _.bind(this.executeDiff, this));
        cider.events.on('//socket/message/s', _.bind(function() {
            this.setDirty(false);
        }, this));
        cider.events.on('//editor/find', _.bind(this.find, this));
        cider.events.on(
            '//editor/find/previous',
            _.bind(this.findPrevious, this)
        );
        cider.events.on('//editor/find/next', _.bind(this.findNext, this));
    },
    render: function() {
        var context = _.pick(this.options || {}, ['text']);
        context = _.defaults(context, {text: ''});
        this.$el.html(this.template(context));
        return this;
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
                cider.events.trigger('//editor/save');
            }
        });

        this.editor.commands.addCommand({
            name: 'find',
            bindKey: {win: 'Ctrl-F', mac: 'Command-F'},
            exec: function() {
                cider.events.trigger('//search');
            }
        });

        this.editor.commands.addCommand({
            name: 'findNext',
            bindKey: {win: 'Ctrl-G', mac: 'Command-G'},
            exec: function() {
                cider.events.trigger('//editor/find/next');
            }
        });

        this.editor.commands.addCommand({
            name: 'findPrevious',
            bindKey: {win: 'Ctrl-Shift-G', mac: 'Command-Shift-G'},
            exec: function() {
                cider.events.trigger('//editor/find/previous');
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
                    this.setTabWidth(this.preferences.get('stwm', 2));
                } else {
                    this.setTabWidth(this.preferences.get('stw', 4));
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
        cider.events.trigger('//editor/change', diff);
        if(!this.socketSuppress) {
            cider.events.trigger('//socket/send', diff);
        }
    },
    prepareSave: function() {
        if(this.preferences.get('sttws')) {
            this.trimLines();
        }
        if(this.preferences.get('ssn')) {
            this.trimToSingleNewline();
        }
        this.setDirty(false);
        cider.events.trigger('//file/save', this.getText());
    },
    handleSaved: function(response) {
        if(!response.success) {
            if(!this.isDirty()) {
                this.revertDirty();
            }
        }
        if(!this.isDirty()) {
            cider.events.trigger('//editor/clean');
        } else {
            cider.events.trigger('//editor/dirty');
        }
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

cider.views.editor.FindBar = Backbone.View.extend({
    events: {
        'click #find-previous-btn': 'findPrevious',
        'click #find-next-btn': 'findNext',
        'keyup #find': 'find'
    },
    template: _.template(cider.templates.editor.FIND_BAR),
    initialize: function() {
        cider.events.on('//search', _.bind(this.search, this));
    },
    render: function() {
        this.$el.html(this.template());
        return this;
    },
    search: function() {
        var element = $('#find');
        element.select();
        this.find();
    },
    find: function() {
        var element = $('#find');
        if(element.val() !== '') {
            cider.events.trigger('//editor/find', element.val());
        }
    },
    findPrevious: function() {
        cider.events.trigger('//editor/find/previous');
    },
    findNext: function() {
        cider.events.trigger('//editor/find/next');
    }
});

cider.views.editor.Settings = Backbone.View.extend({
    events: {
        'change #stw': 'handleIntSetting',
        'change #stwm': 'handleIntSetting',
        'change #shm': 'handleModeSetting',
        'change #sttws': 'handleBooleanSetting',
        'change #ssn': 'handleBooleanSetting'
    },
    template: _.template(cider.templates.editor.SETTINGS),
    preferences: null,
    initialize: function() {
        this.preferences = new cider.Preferences();
        cider.events.on('//settings/show', _.bind(this.showSettings, this))
    },
    render: function() {
        var context = _.pick(this.options || {}, ['mode', 'modes']);
        context = _.defaults(context, {mode: 'text'});
        context.stw = this.preferences.get('stw', 4);
        context.stwm = this.preferences.get('stwm', 2);
        context.sttws = this.preferences.get('sttws', false);
        context.ssn = this.preferences.get('ssn', false);
        this.$el.html(this.template(context));
        return this;
    },
    handleBooleanSetting: function(e) {
        this.preferences.set(
            $(e.target).attr('id'),
            $(e.target).is(':checked')
        );
    },
    handleIntSetting: function(e) {
        this.preferences.set(
            $(e.target).attr('id'),
            parseInt($(e.target).val())
        );
    },
    handleModeSetting: function(e) {
        this.preferences.set(
            this.options.highlight_mode_key,
            $(e.target).val()
        );
    },
    showSettings: function() {
        $('#settings').modal('show');
    }
});
