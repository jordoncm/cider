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

cider.editor.File = cider.extend();

cider.editor.File.prototype.file = null;
cider.editor.File.prototype.externalSaveCallback = null;
cider.editor.File.prototype.saving = false;

cider.editor.File.prototype.save = function(text, parameters) {
    if(!parameters) {
        parameters = {};
    }
    
    parameters.file = this.file;
    parameters.text = text;
    
    this.saving = true;
    $.ajax({
        url : '../save-file/',
        type : 'POST',
        dataType : 'json',
        data : parameters,
        success : _.bind(function(response) {
            this.saveCallback(response);
        }, this)
    });
};

cider.editor.File.prototype.saveCallback = function(response) {
    this.externalSaveCallback(response);
    this.saving = false;
};

cider.editor.File.prototype.isSaving = function() {
    return this.saving;
};

cider.editor.File.prototype.init = function(config) {
    this.file = config.file;
    if(typeof config.saveCallback != 'undefined') {
        this.externalSaveCallback = config.saveCallback;
    }
};