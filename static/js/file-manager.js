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

function getCreateParameter() {
    var name = document.getElementById('name').value;
    
    var parameter = '';
    if(path != '') {
        parameter = path + '/' + name;
    } else {
        parameter = name;
    }
    
    return parameter;
}

function createFile() {
    var parameter = getCreateParameter();
    
    if(document.getElementById('name').value != '') {
        window.open(
            '../editor/?file=' + encodeURIComponent(parameter),
            '_blank'
        );
    }
    
    return false;
}

function createFolder() {
    var parameter = getCreateParameter();
    
    if(document.getElementById('name').value != '') {
        $.getJSON(
            '../create-folder/',
            {
                path : parameter
            },
            function(json) {
                if(json.success) {
                    window.location.reload();
                } else {
                    alert('Folder creation failed.');
                }
            }
        );
    }
    
    return false;
}

function confirmOpen(type) {
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
}