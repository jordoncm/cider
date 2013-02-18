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

cider.namespace('cider.editor');

cider.editor.File = cider.extend();

cider.editor.File.prototype.file = null;
cider.editor.File.prototype.salt = null;
cider.editor.File.prototype.extra = null;
cider.editor.File.prototype.saving = false;
cider.editor.File.prototype.readOnly = false;

cider.editor.File.prototype.save = function(text) {
    if(!this.readOnly) {
        var parameters = {};
        var tmp = this.extra.split('&');
        for(var i = 0; i < tmp.length; i++) {
            if(tmp[i] !== '') {
                try {
                    tmp[i] = tmp[i].split('=');
                    parameters[tmp[i][0]] = tmp[i][1];
                } catch(e) {}
            }
        }
        parameters.salt = this.salt;
        parameters.file = this.file;
        parameters.text = text;

        this.saving = true;
        $.ajax({
            url : '../save-file/',
            type : 'POST',
            dataType : 'json',
            data : parameters,
            success : _.bind(this.saveCallback, this)
        });
    } else {
        console.warn('File is read only and cannot be saved.');
    }
};

cider.editor.File.prototype.saveCallback = function(response) {
    this.saving = false;
    cider.events.publish('//file/saved', response);
};

cider.editor.File.prototype.hash = function(salt) {
    var input = this.file;
    if(salt) {
        input += salt;
    }
    var hash = 0;
    if(input.length) {
        for(var i = 0; i < input.length; i++) {
            var char = input.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
    }
    return hash;
};

cider.editor.File.prototype.isSaving = function() {
    return this.saving;
};

cider.editor.File.prototype.initialize = function(config) {
    this.file = config.file;
    this.salt = config.salt;
    this.extra = config.extra;
    this.readOnly = config.read_only;
    cider.events.subscribe('//file/save', _.bind(this.save, this));
};

cider.editor.Socket = cider.extend();

cider.editor.Socket.prototype.socket = null;
cider.editor.Socket.prototype.suppress = false;
cider.editor.Socket.prototype.name = null;
cider.editor.Socket.prototype.salt = null;
cider.editor.Socket.prototype.file = null;

cider.editor.Socket.prototype.generateId = function(prefix) {
    var text = prefix || '';
    var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for(var i = 0; i < 5; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
};

cider.editor.Socket.prototype.send = function(m) {
    if(!this.suppress) {
        this.socket.send(JSON.stringify(m));
    }
};

cider.editor.Socket.prototype.handleOpen = function() {
    this.send({t: 'f', f: this.file, v: -1, n: this.name, s: this.salt});
    cider.events.publish('//socket/open');
    cider.events.subscribe('//socket/send', _.bind(this.send, this));
};

cider.editor.Socket.prototype.handleMessage = function(m) {
    console.log(m.data);
    var dataList = JSON.parse(m.data);
    for(var i = 0; i < dataList.length; i++) {
        var data = dataList[i];
        cider.events.publish('//socket/message/' + data.t, data);
    }
};

cider.editor.Socket.prototype.initialize = function(config) {
    if(typeof config.name != 'undefined' && config.name) {
        this.name = config.name;
    } else {
        this.name = this.generateId('cider-');
    }

    this.file = config.file;
    this.salt = config.salt;

    this.socket = new WebSocket('ws://' + location.host + '/ws/');
    this.socket.onopen = _.bind(this.handleOpen, this);
    this.socket.onmessage = _.bind(this.handleMessage, this);
    this.socket.onerror = function(e) {
        console.log('socket error');
        console.log(e);
    };
    this.socket.onclose = function(e) {
        console.log('socket close');
        console.log(e);
    };
};
