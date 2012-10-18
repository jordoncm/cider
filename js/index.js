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
    $('body').append(new cider.views.index.Content().render(config));
    $('body').append(new cider.views.BottomNav().render({
        right_content: new cider.views.index.BottomNavRight().render()
    }));

    var prefs = new cider.Preferences();
    $('#sname').val(prefs.get('sname'));
    $('#sname').on('keyup', function() {
        var value = $('#sname').val();
        if(value !== '') {
            prefs.set('sname', value);
        } else {
            prefs.remove('sname');
        }
    });

    if(config.enable_sftp) {
        $('#sftpf').on('submit', function() {
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
        });

        $('#sftp-launch').on('click', function() {
            $('#sftp').modal('show');
        });

        $('#sftp-connect').on('click', function() {
            $('#sftpf').submit();
        });

        $('#sftp-cancel').on('click', function() {
            $('#sftp').modal('hide');
        });
    }
});
