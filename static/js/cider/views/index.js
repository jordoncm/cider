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
    events: {
        'keyup #sname': 'setSessionName',
        'submit #sftpf': 'handleSftpSubmit',
        'click #sftp-launch': 'sftpShow',
        'click #sftp-connect': 'sftpSubmit',
        'click #sftp-cancel': 'sftpHide'
    },
    template: _.template(cider.templates.index.CONTENT),
    preferences: null,
    initialize: function() {
        this.preferences = new cider.Preferences();
    },
    render: function(context) {
        context = context || {};
        context = _.defaults(context, {sname: this.preferences.get('sname')});
        this.$el.html(this.template(context));
        return this;
    },
    setSessionName: function(e) {
        var value = $(e.target).val();
        if(value !== '') {
            this.preferences.set('sname', value);
        } else {
            this.preferences.remove('sname');
        }
    },
    handleSftpSubmit: function() {
        try {
            var valid = true;
            var text = 'Please correct the following:';
            if($('#sftp_host').val() === '') {
                valid = false;
                text += '\n - Enter a hostname.';
            }

            if(!valid) {
                alert(text);
            }
            return valid;
        } catch(e) {
            return false;
        }
    },
    sftpShow: function() {
        $('#sftp').modal('show');
    },
    sftpSubmit: function() {
        $('#sftpf').submit();
    },
    sftpHide: function() {
        $('#sftp').modal('hide');
    }
});

cider.views.index.BottomNavRight = Backbone.View.extend({
    template: _.template(cider.templates.index.BOTTOM_RIGHT_NAV),
    render: function(context) {
        this.$el.html(this.template(context));
        return this;
    }
});
