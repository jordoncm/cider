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

cider.namespace('cider.views.editor');

cider.views.editor.Menu = Backbone.View.extend({
    template: _.template(cider.templates.editor.MENU),
    render: function() {
        var context = _.pick(
            this.options || {},
            ['save_text', 'save_class', 'file']
        );
        context = _.defaults(context, {
            save_text: 'Save',
            save_class: 'btn-warning',
            file: ''
        });
        this.$el.html(this.template(context));
        return this;
    }
});

cider.views.editor.Editor = Backbone.View.extend({
    template: _.template(cider.templates.editor.EDITOR),
    render: function() {
        var context = _.pick(this.options || {}, ['text']);
        context = _.defaults(context, {text: ''});
        this.$el.html(this.template(context));
        return this;
    }
});

cider.views.editor.FindBar = Backbone.View.extend({
    template: _.template(cider.templates.editor.FIND_BAR),
    render: function() {
        this.$el.html(this.template());
        return this;
    }
});

cider.views.editor.Settings = Backbone.View.extend({
    template: _.template(cider.templates.editor.SETTINGS),
    render: function() {
        var context = _.pick(this.options || {}, ['mode']);
        context = _.defaults(context, {mode: 'text'});
        this.$el.html(this.template(context));
        return this;
    }
});
