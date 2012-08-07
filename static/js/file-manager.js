/**
 * This work is copyright 2011 Jordon Mears. All rights reserved.
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

cider.namespace('cider.filemanager');

cider.filemanager.getCreateParameter = function() {
    var name = $('#name').val();
    
    var parameter = '';
    if(path != '') {
        parameter = path + '/' + name;
    } else {
        parameter = name;
    }
    
    return parameter;
};

cider.filemanager.createFile = function() {
    var parameter = cider.filemanager.getCreateParameter();
    
    if($('#name').val() != '') {
        window.open(
            '../editor/?file=' + encodeURIComponent(parameter) + extra,
            '_blank'
        );
    }
    
    return false;
};

cider.filemanager.createFolder = function() {
    var parameter = cider.filemanager.getCreateParameter();
    
    var parameters = {};
    var tmp = extra.split('&');
    for(var i = 0; i < tmp.length; i++) {
        if(tmp[i] != '') {
            try {
                tmp[i] = tmp[i].split('=');
                parameters[tmp[i][0]] = tmp[i][1];
            } catch(e) {}
        }
    }
    parameters.path = parameter;
    
    if($('#name').val() != '') {
        $.getJSON(
            '../create-folder/',
            parameters,
            function(json) {
                if(json.success) {
                    var location = window.location;
                    if(window.location.search == '?') {
                        location += 'folder=' + $('#name').val();
                    } else if(window.location.search != '') {
                        location += '&folder=' + $('#name').val();
                    } else {
                        location += '?folder=' + $('#name').val();
                    }
                    window.location = location + extra;
                } else {
                    alert('Folder creation failed.');
                }
            }
        );
    }
    
    return false;
};

cider.filemanager.confirmOpen = function(type) {
    switch(type) {
        case 'binary':
            return confirm(
                'This appears to be a binary file. Are you sure you want to open it?'
            );
            break;
        case 'large':
            return confirm(
                'This file is larger than 10MB. It may not perform well in the browser. Are you sure you want to open it?'
            );
            break;
        default:
            return true;
    }
};