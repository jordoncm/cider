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

$(function() {
    $('body').append(new cider.views.TopNav().render({
        header: '',
        sub_header: '',
        sub_header_link: '',
        extra: ''
    }));
    $('body').append(new cider.views.Error().render({
        message: config.message
    }));
    $('body').append(new cider.views.BottomNav().render({
        right_content: ''
    }));
});
