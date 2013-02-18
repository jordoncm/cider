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

cider.namespace('cider.views.index');

cider.views.index.Content = cider.views.View.extend({
    events: {
        'keyup #sname': 'setSessionName',
        'submit #sftpf': 'handleSftpSubmit',
        'click #sftp-launch': 'sftpShow',
        'click #sftp-connect': 'sftpSubmit',
        'click #sftp-cancel': 'sftpHide'
    },
    template: _.template(cider.templates.index.CONTENT),
    contextSchema: [
        'enable_dropbox',
        'enable_local_file_system',
        'enable_sftp',
        'sname',
        'terminal_link'
    ],
    contextDefaults: {sname: cider.Preferences.get('sname')},
    setSessionName: function(e) {
        var value = $(e.target).val();
        if(value !== '') {
            cider.Preferences.set('sname', value);
        } else {
            cider.Preferences.remove('sname');
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

cider.views.index.BottomNavRight = cider.views.View.extend({
    template: _.template(cider.templates.index.BOTTOM_RIGHT_NAV)
});
