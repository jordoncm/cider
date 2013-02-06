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

cider.namespace('cider.views.index');

cider.views.index.Content = Backbone.View.extend({
    template: _.template(cider.templates.index.CONTENT),
    render: function(context) {
        this.$el.html(this.template(context));
        return this;
    }
});

cider.views.index.BottomNavRight = Backbone.View.extend({
    template: _.template(cider.templates.index.BOTTOM_RIGHT_NAV),
    render: function(context) {
        this.$el.html(this.template(context));
        return this;
    }
});
