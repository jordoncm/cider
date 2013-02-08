/**
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

cider.namespace('cider.views.filemanager');

cider.views.filemanager.NewFolder =  Backbone.View.extend({
    template: _.template(cider.templates.filemanager.NEW_FOLDER),
    render: function() {
        this.$el.html(this.template());
        return this;
    }
});

cider.views.filemanager.FileList = Backbone.View.extend({
    events: {
        'click [id^=file-icon], [id^=file-name], [id^=file-button]': 'confirmOpen'
    },
    template: _.template(cider.templates.filemanager.FILE_LIST),
    templateFolder: _.template(cider.templates.filemanager.FOLDER_ROW),
    templateFile: _.template(cider.templates.filemanager.FILE_ROW),
    render: function() {
        var context = _.pick(
            this.options || {},
            ['path', 'up', 'extra', 'rows']
        );
        context = _.defaults(context, {
            path: '',
            up: '',
            extra: '',
            rows: ''
        });

        var rows = [];
        for(var i = 0; i < this.options.files_list.length; i++) {
            var file = this.options.files_list[i];
            if(file.is_file) {
                rows.push(this.templateFile({
                    i: i,
                    extra: config.extra,
                    file: file,
                    path_file_name: (config.path) ? config.path + '/' + file.name : file.name
                }));
            } else {
                rows.push(this.templateFolder({
                    extra: config.extra,
                    file: file,
                    path_file_name: (config.path) ? config.path + '/' + file.name : file.name
                }));
            }
        }
        context = _.extend(context, {rows: rows.join('')});
        this.$el.html(this.template(context));
        return this;
    },
    confirmOpen: function(e) {
        var type = this.options.files_list[
            e.target.id.split('-')[e.target.id.split('-').length - 1]
        ].confirm;
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
    }
});

cider.views.filemanager.CreateFileFolder =  Backbone.View.extend({
    events: {
        'click #new-file': 'createFile',
        'click #new-folder': 'createFolder',
        'submit #new-form': 'createFile'
    },
    template: _.template(cider.templates.filemanager.CREATE_FILE_FOLDER),
    render: function() {
        this.$el.html(this.template());
        return this;
    },
    getCreateParameter: function() {
        var name = $('#name').val();

        var parameter = '';
        if(config.path !== '') {
            parameter = config.path + '/' + name;
        } else {
            parameter = name;
        }

        return parameter;
    },
    createFile: function() {
        var parameter = this.getCreateParameter();

        if($('#name').val() !== '') {
            window.open(
                '../editor/?file=' + encodeURIComponent(parameter) + config.extra,
                '_blank'
            );
        }

        return false;
    },
    createFolder: function() {
        var parameter = this.getCreateParameter();

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
    }
});
