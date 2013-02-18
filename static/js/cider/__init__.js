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

if(typeof cider != 'object') {
    var cider = {};
}

/**
 * Ensures given namespace is declared.
 *
 * @param {String} ns String of the namespace to declare.
 */
cider.namespace = function(ns) {
    if(ns && ns !== '') {
        var parent = cider;
        ns = ns.split('.');
        for(var i = 0; i < ns.length; i++) {
            if(i !== 0 || ns[i] != 'cider') {
                if(typeof parent[ns[i]] == 'undefined') {
                    parent[ns[i]] = {};
                }
                parent = parent[ns[i]];
            }
        }
    }
};

/**
 * Default constructor for creating class definitions.
 *
 * Handles delcaring inheritance and looks for method called initialize to
 * execute on object creation.
 *
 * @param {function} The constructor this class should extend.
 * @return {function} The constructor for the class.
 */
cider.extend = function(parent) {
    var cls = function(config) {
        if(this.initialize) {
            this.initialize(config);
        }
    };
    if(parent) {
        cls.prototype = new parent();
        cls.prototype.constructor = cls;
    }
    return cls;
};

/**
 * A global events object instance to provide basic pub/sub capability in the
 * UI.
 */
cider.events = _.extend({}, Backbone.Events);

/**
 * Fetches a given key from the query string.
 *
 * @param {String} key The key to look for.
 * @param [defaultValue] Optional default value to return if the key is not
 * found.
 * @return The value from the query string or the default.
 */
cider.argument = function(key, defaultValue) {
    var args = {};
    var list = window.location.search.replace(/^\?/, '').split('&');
    for(var i = 0; i < list.length; i++) {
        var item = list[i].split('=');
        if(item.length > 1) {
            args[item[0]] = item[1];
        }
    }
    return (args[key] !== undefined) ? args[key] : defaultValue;
};

/**
 * Class that manages a key/value store for keeping user preferences.
 *
 * @constructor
 */
cider.Preferences = cider.extend();

/**
 * Fetch a value by its key.
 *
 * This method will automatically deserialize JSON strings into objects.
 *
 * @param {String} key The key lookup.
 * @param [defaultValue] Optional default value to return if the key is not
 * found.
 * @return The value in the local store, the given default value or null.
 */
cider.Preferences.prototype.get = function(key, defaultValue) {
    var value = localStorage.getItem(key);
    if(value) {
        try {
            return JSON.parse(value);
        } catch(e) {}
    }
    return (value !== null) ? value : defaultValue;
};

/**
 * Set a value into the local store.
 *
 * This will override existing values in the store. Will also automatically
 * serialize objects into JSON strings for storing. Triggers an event named
 * after the key if the value has changed from the previously stored value.
 *
 * @param {String} key The key to store the value under.
 * @param {String} value The value to store.
 */
cider.Preferences.prototype.set = function(key, value) {
    var oldValue = localStorage.getItem(key);
    if(typeof value == 'object') {
        localStorage.setItem(key, JSON.stringify(value));
    } else {
        localStorage.setItem(key, value);
    }
    if(value !== oldValue) {
        cider.events.trigger('//preferences/' + key, value);
    }
};

/**
 * Remove an item from the store.
 *
 * Will trigger an event named after the key providing the value null.
 *
 * @param {String} key Key of the value to remove.
 */
cider.Preferences.prototype.remove = function(key) {
    localStorage.removeItem(key);
    cider.events.trigger('//preferences/' + key, null);
};
