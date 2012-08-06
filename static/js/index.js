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

cider.namespace('cider.index');

cider.index.updateSessionName = function(value) {
    if(value !== '') {
        preferencesObj.set('sname', value);
    } else {
        preferencesObj.remove('sname');
    }
};

cider.index.initSessionName = function() {
    var tmp = preferencesObj.get('sname');
    if(tmp) {
        $('#sname').val(tmp);
    }
};

cider.index.sftpValidate = function() {
    try {
        var valid = true;
        var text = 'Please correct the following:';
        if($('#sftp_host').val() == '') {
            valid = false;
            text += '\n - Enter a hostname.'
        }
        
        if(!valid) {
            alert(text);
        }
        return valid;
    } catch(e) {
        return false;
    }
};

var preferencesObj = new cider.Preferences();

$(function() {
    cider.index.initSessionName();
});