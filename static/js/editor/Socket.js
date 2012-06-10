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

cider.editor.Socket = function(config) {
    this.socket = null;
    this.suppress = false;
    this.openCallback = null;
    this.messageCallback = null;
    
    this.send = function(m) {
        if(!this.suppress) {
            this.socket.send(JSON.stringify(m));
        }
    };
    
    this.handleOpen = function() {
        if(this.openCallback) {
            this.openCallback();
        }
    };
    
    this.handleMessage = function(m) {
        if(this.messageCallback) {
            this.messageCallback(m);
        }
    };
    
    this.init = function(config) {
        var closure = this;
        
        if(typeof config.openCallback != 'undefined') {
            this.openCallback = config.openCallback;
        }
        
        if(typeof config.messageCallback != 'undefined') {
            this.messageCallback = config.messageCallback;
        }
        
        this.socket = new WebSocket('ws://' + location.host + '/ws/');
        this.socket.onopen = function() {
            closure.handleOpen();
        };
        this.socket.onmessage = function(m) {
            closure.handleMessage(m);
        };
        this.socket.onerror = function(e) {
            console.log('socket error');
            console.log(e);
        };
        this.socket.onclose = function(e) {
            console.log('socket close');
            console.log(e);
        };
    };
    this.init(config);
};