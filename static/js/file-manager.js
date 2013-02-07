/**
 * This work is copyright 2012 - 2013 Jordon Mears. All rights reserved.
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

$(function() {
    var Router = Backbone.Router.extend({
        routes: {
            '*splat': 'index'
        },
        index: function() {
            $('body').append(new cider.views.TopNav().render({
                header: config.prefix + (
                    (config.path) ? config.path : '&nbsp;'
                ),
                sub_header: '',
                sub_header_link: '',
                extra: ''
            }).$el);
            if(config.folder) {
                $('body').append(
                    new cider.views.filemanager.NewFolder().render({
                        folder: config.folder
                    }).$el
                );
            }
            $('body').append(new cider.views.filemanager.FileList().render({
                path: config.path,
                up: config.up,
                extra: config.extra,
                files_list: config.files_list
            }).$el);
            $('body').append(new cider.views.BottomNav().render({
                right_content: new cider.views.filemanager.CreateFileFolder()
            }).$el);
        }
    });
    router = new Router();
    Backbone.history.start();
});
