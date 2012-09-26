$(function() {
    $('body').append(new cider.views.TopNav().render({
        header: '',
        sub_header: '',
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