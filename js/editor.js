var save = function() {
    $('#save').html('Saving...');
    editorObj.setDirty(false);
    var parameters = {};
    var tmp = config.extra.split('&');
    for(var i = 0; i < tmp.length; i++) {
        if(tmp[i] != '') {
            try {
                tmp[i] = tmp[i].split('=');
                parameters[tmp[i][0]] = tmp[i][1];
            } catch(e) {}
        }
    }
    parameters.salt = config.salt;
    fileObj.save(editorObj.getText(), parameters);
};

var saveCallback = function(response) {
    if(!response.success) {
        if(!editorObj.isDirty()) {
            editorObj.revertDirty();
        }
    }
    
    if(!editorObj.isDirty()) {
        $('#save').removeClass('btn-warning');
        $('#save').addClass('btn-success');
        $('#save').html('Saved');
    } else {
        $('#save').removeClass('btn-success');
        $('#save').addClass('btn-warning');
        $('#save').html('Save');
    }
};

var makeSaved = function() {
    editorObj.setDirty(false);
    $('#save').removeClass('btn-warning');
    $('#save').addClass('btn-success');
    $('#save').html('Saved');
};

var setTabWidth = function(width) {
    editorObj.setTabWidth(width);
};

var setHighlightMode = function(mode) {
    editorObj.setMode(mode);
};

var find = function() {
    var element = $('#find');
    element.select();
    if(element.val() !== '') {
        search(element.val());
    }
};

var findNext = function() {
    editorObj.findNext();
};

var findPrevious = function() {
    editorObj.findPrevious();
};

var search = function(needle) {
    if(needle && needle !== '') {
        editorObj.find(needle);
    }
    
    return false;
};

var initTabWidth = function() {
    var tmp = preferencesObj.get('stw');
    if(tmp) {
        $('#stw').val(preferencesObj.get('stw'));
        if(!config.markup) {
            setTabWidth(parseInt(tmp));
        }
    }
    tmp = preferencesObj.get('stwm');
    if(tmp) {
        $('#stwm').val(preferencesObj.get('stwm'));
        if(config.markup) {
            setTabWidth(parseInt(tmp));
        }
    }
};

var saveTabWidth = function(type, width) {
    if(config.markup && type == 'stwm') {
        setTabWidth(width);
    }
    if(!config.markup && type == 'stw') {
        setTabWidth(width);
    }
    preferencesObj.set(type, width);
};

var generateId = function() {
    var text = '';
    var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for(var i = 0; i < 5; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
};

var editorObj = null;
var fileObj = null;
var socketObj = null;
var preferencesObj = null;

$(function() {
    $('body').append(new cider.views.TopNav().render({
        header: config.file_name,
        sub_header: config.prefix + config.path,
        extra: new cider.views.editor.Menu().render({
            save_text: config.save_text,
            save_class: (config.save_text.toLowerCase() == 'saved') ? 'btn-success' : 'btn-warning',
            file: config.file
        })
    }));
    
    $('body').append(new cider.views.editor.Editor().render({
        text: config.text
    }));
    
    $('body').append(new cider.views.BottomNav().render({
        right_content: new cider.views.editor.FindBar().render()
    }));
    
    $('body').append(new cider.views.editor.Settings().render({
        mode: config.mode
    }));
    
    $('#save').on('click', save);
    $('#settings-btn').on('click', function() {
        $('#settings').modal('show');
    });
    
    var editorSettings = {
        editorId : 'editor',
        tabWidth : config.tabWidth,
        shortcuts : {
            save : save,
            find : find
        },
        change : function(e, diff) {
            $('#save').removeClass('btn-success');
            $('#save').addClass('btn-warning');
            $('#save').html('Save');
            socketObj.send(diff);
        }
    };
    if(typeof config.mode != 'undefined') {
        editorSettings.mode = config.mode;
    }
    editorObj = new cider.editor.Editor(editorSettings);
    
    fileObj = new cider.editor.File({
        file : config.file,
        saveCallback : saveCallback
    });
    
    preferencesObj = new cider.Preferences();
    
    initTabWidth();
    
    try {
        socketObj = new cider.editor.Socket({
            openCallback : function() {
                var kvp = location.search.substr(1).split('&');
                var args = {};
                for(var i = 0; i < kvp.length; i++) {
                    try {
                        var tmp = kvp[i].split('=');
                        args[tmp[0]] = tmp[1];
                    } catch(e) {}
                }
                var name = preferencesObj.get('sname');
                if(!name) {
                    name = 'cider-' + generateId();
                }
                socketObj.send(
                    {t : 'f', f : args.file, v : -1, n : name, s : config.salt}
                );
                editorObj.setReadOnly(false);
            },
            messageCallback : function(m) {
                console.log(m.data);
                var dataList = JSON.parse(m.data);
                for(var i = 0; i < dataList.length; i++) {
                    var data = dataList[i];
                    socketObj.suppress = true;
                    switch(data.t) {
                        case 'd':
                        case 'i':
                            editorObj.executeDiff(data);
                            break;
                        case 's':
                            makeSaved();
                            break;
                        case 'n':
                            $('#editors-title').html(data.n.length + ' editors');
                            $('#editors-list li').remove();
                            for(var j = 0; j < data.n.length; j++) {
                                $('#editors-list').append(
                                    '<li><a>' + data.n[j] + '</a></li>'
                                );
                            }
                            break;
                    }
                    socketObj.suppress = false;
                }
            }
        });
    } catch(e) {
        editorObj.setReadOnly(false);
        console.log(e);
    }
    
    $('#find').on('keyup', function() {
        search($('#find').val());
    });
    $('#find-next-btn').on('click', findNext);
    $('#find-previous-btn').on('click', findPrevious);
    
    window.onbeforeunload = function() {
        /* $(window).unload does not appear to be consistent. */
        if(editorObj.isDirty()) {
            return 'Document has unsaved changes; changes will be lost.';
        }
        
        if(fileObj.isSaving()) {
            return 'Save operation in progress; changes could be lost.';
        }
    };
    
    $(window).keydown(function(e) {
        if(e.ctrlKey || e.metaKey) {
            switch(e.keyCode) {
                case 'F'.charCodeAt(0):
                    e.preventDefault();
                    find();
                    break;
                case 'G'.charCodeAt(0):
                    e.preventDefault();
                    if(e.shiftKey) {
                        findPrevious();
                    } else {
                        findNext();
                    }
                    break;
                case 'S'.charCodeAt(0):
                    e.preventDefault();
                    save();
                    break;
            }
        }
    });
});