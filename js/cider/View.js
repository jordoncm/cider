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

cider.namespace('cider');

cider.View = cider.extend();

cider.View.prototype.templateCode = '';

cider.View.prototype.template = null;

cider.View.prototype.init = function(config) {
    this.template = _.template(this.templateCode);
};

cider.View.prototype.render = function(data) {
    if(data) {
        return this.template(data);
    } else {
        return this.template();
    }
};
