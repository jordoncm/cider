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

var getCreateParameter = function() {
    var name = $('#name').val();

    var parameter = '';
    if(config.path !== '') {
        parameter = config.path + '/' + name;
    } else {
        parameter = name;
    }

    return parameter;
};

var createFile = function() {
    var parameter = getCreateParameter();

    if($('#name').val() !== '') {
        window.open(
            '../editor/?file=' + encodeURIComponent(parameter) + config.extra,
            '_blank'
        );
    }

    return false;
};

var createFolder = function() {
    var parameter = getCreateParameter();

    var parameters = {};
    var tmp = config.extra.split('&');
    for(var i = 0; i < tmp.length; i++) {
        if(tmp[i] !== '') {
            try {
                tmp[i] = tmp[i].split('=');
                parameters[tmp[i][0]] = tmp[i][1];
            } catch(e) {}
        }
    }
    parameters.path = parameter;

    if($('#name').val() !== '') {
        $.getJSON(
            '../create-folder/',
            parameters,
            function(json) {
                if(json.success) {
                    var location = window.location;
                    if(window.location.search == '?') {
                        location += 'folder=' + $('#name').val();
                    } else if(window.location.search !== '') {
                        location += '&folder=' + $('#name').val();
                    } else {
                        location += '?folder=' + $('#name').val();
                    }
                    window.location = location + config.extra;
                } else {
                    alert('Folder creation failed.');
                }
            }
        );
    }

    return false;
};

var confirmOpen = function(type) {
    switch(type) {
        case 'binary':
            return confirm(
                'This appears to be a binary file. Are you sure you want to open it?'
            );
        case 'large':
            return confirm(
                'This file is larger than 10MB. It may not perform well in the browser. Are you sure you want to open it?'
            );
        default:
            return true;
    }
};

$(function() {
    $('body').append(new cider.views.TopNav().render({
        header: config.prefix + ((config.path) ? config.path : '&nbsp;'),
        sub_header: '',
        sub_header_link: '',
        extra: ''
    }));
    if(config.folder) {
        $('body').append(new cider.views.filemanager.NewFolder().render({
            folder: config.folder
        }));
    }
    var rows = [];
    var fileTemplate = null;
    var folderTemplate = null;
    for(var i = 0; i < config.files_list.length; i++) {
        var file = config.files_list[i];
        if(file.is_file) {
            if(!fileTemplate) {
                fileTemplate = new cider.views.filemanager.FileRow();
            }
            rows.push(fileTemplate.render({
                i: i,
                extra: config.extra,
                file: file,
                path_file_name: (config.path) ? config.path + '/' + file.name : file.name
            }));
        } else {
            if(!folderTemplate) {
                folderTemplate = new cider.views.filemanager.FolderRow();
            }
            rows.push(folderTemplate.render({
                extra: config.extra,
                file: file,
                path_file_name: (config.path) ? config.path + '/' + file.name : file.name
            }));
        }
    }
    $('body').append(new cider.views.filemanager.FileList().render({
        path: config.path,
        up: config.up,
        extra: config.extra,
        rows: rows.join('')
    }));
    $('body').append(new cider.views.BottomNav().render({
        right_content: new cider.views.filemanager.CreateFileFolder().render()
    }));

    for(var i = 0; i < config.files_list.length; i++) {
        var file = config.files_list[i];
        if(file.is_file) {
            $('#file-icon-' + i + ', #file-name-' + i + ', #file-button-' + i).on('click', _.bind(function() {
                return confirmOpen(this.confirm);
            }, file));
        }
    }

    $('#new-file').on('click', function() {
        return createFile();
    });

    $('#new-folder').on('click', function() {
        return createFolder();
    });

    $('#new-form').on('submit', function() {
        return createFile();
    });
});
