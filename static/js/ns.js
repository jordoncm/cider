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

if(typeof cider != 'object') {
    var cider = {};
}

cider.namespace = function(ns) {
    if(ns && ns !== '') {
        var parent = cider;
        ns = ns.split('.');
        for(var i = 0; i < ns.length; i++) {
            if(i !== 0 || ns[i] != 'cider') {
                if(typeof parent[ns[i]] == 'undefined') {
                    parent[ns[i]] = {};
                }
                parent = parent[ns[i]];
            }
        }
    }
};