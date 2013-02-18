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

$(function() {
    var Router = Backbone.Router.extend({
        routes: {
            '*splat': 'index'
        },
        index: function() {
            var file = new cider.editor.File({
                file: config.file,
                salt: config.salt,
                extra: config.extra
            });

            // Change config values based on user preferences.
            config.mode = cider.Preferences.get(
                'fm-' + file.hash(config.salt),
                config.mode
            );
            config.tab_width = (config.markup) ? cider.Preferences.get(
                'stwm',
                config.tab_width
            ) : cider.Preferences.get('stw', config.tab_width);

            $('body').append(new cider.views.TopNav({
                header: config.file_name,
                sub_header: config.prefix + config.path,
                sub_header_link: '../file-manager/?path=' + config.path + config.extra,
                extra: new cider.views.editor.Menu({
                    save_text: config.save_text,
                    save_class: (config.save_text.toLowerCase() == 'saved') ? 'btn-success' : 'btn-warning',
                    file: config.file,
                    extra: config.extra
                })
            }).render().$el);
            var editor = new cider.views.editor.Editor({
                text: config.text,
                tab_width: config.tab_width,
                markup: config.markup,
                mode: (config.mode !== undefined) ? config.mode : null,
                modes: config.modes,
                highlight_mode_key: 'fm-' + file.hash(config.salt)
            });
            $('body').append(editor.render().$el);
            editor.renderEditor();
            $('body').append(new cider.views.BottomNav({
                right_content: new cider.views.editor.FindBar()
            }).render().$el);
            $('body').append(new cider.views.editor.Settings({
                markup: config.markup,
                mode: config.mode,
                modes: config.modes,
                highlight_mode_key: 'fm-' + file.hash(config.salt)
            }).render().$el);
            $('body').append(new cider.views.editor.Permalink().render().$el);

            var socket = null;
            try {
                socket = new cider.editor.Socket({
                    name: cider.Preferences.get('sname'),
                    file: config.file,
                    salt: config.salt
                });
            } catch(e) {
                editor.setReadOnly(false);
                console.log(e);
            }

            window.onbeforeunload = function() {
                /* $(window).unload does not appear to be consistent. */
                if(editor.isDirty()) {
                    return 'Document has unsaved changes; changes will be lost.';
                }

                if(file.isSaving()) {
                    return 'Save operation in progress; changes could be lost.';
                }
            };

            $(window).keydown(function(e) {
                if(e.ctrlKey || e.metaKey) {
                    switch(e.keyCode) {
                        case 'F'.charCodeAt(0):
                            e.preventDefault();
                            cider.events.publish('//search');
                            break;
                        case 'G'.charCodeAt(0):
                            e.preventDefault();
                            if(e.shiftKey) {
                                cider.events.publish('//editor/find/previous');
                            } else {
                                cider.events.publish('//editor/find/next');
                            }
                            break;
                        case 'S'.charCodeAt(0):
                            e.preventDefault();
                            cider.events.publish('//editor/save');
                            break;
                    }
                }
            });

            editor.focus();
        }
    });
    router = new Router();
    Backbone.history.start();
});
