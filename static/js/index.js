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
                header: '',
                sub_header: '',
                sub_header_link: '',
                extra: ''
            }).$el);
            $('body').append(
                new cider.views.index.Content().render(config).$el
            );
            $('body').append(new cider.views.BottomNav().render({
                right_content: new cider.views.index.BottomNavRight().render().$el.html()
            }).$el);
        }
    });
    router = new Router();
    Backbone.history.start();
});
