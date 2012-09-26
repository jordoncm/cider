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

cider.editor.Socket = cider.extend();

cider.editor.Socket.prototype.socket = null;
cider.editor.Socket.prototype.suppress = false;
cider.editor.Socket.prototype.openCallback = null;
cider.editor.Socket.prototype.messageCallback = null;

cider.editor.Socket.prototype.send = function(m) {
    if(!this.suppress) {
        this.socket.send(JSON.stringify(m));
    }
};

cider.editor.Socket.prototype.handleOpen = function() {
    if(this.openCallback) {
        this.openCallback();
    }
};

cider.editor.Socket.prototype.handleMessage = function(m) {
    if(this.messageCallback) {
        this.messageCallback(m);
    }
};

cider.editor.Socket.prototype.init = function(config) {
    if(typeof config.openCallback != 'undefined') {
        this.openCallback = config.openCallback;
    }
    
    if(typeof config.messageCallback != 'undefined') {
        this.messageCallback = config.messageCallback;
    }
    
    this.socket = new WebSocket('ws://' + location.host + '/ws/');
    this.socket.onopen = _.bind(function() {
        this.handleOpen();
    }, this);
    this.socket.onmessage = _.bind(function(m) {
        this.handleMessage(m);
    }, this);
    this.socket.onerror = function(e) {
        console.log('socket error');
        console.log(e);
    };
    this.socket.onclose = function(e) {
        console.log('socket close');
        console.log(e);
    };
};