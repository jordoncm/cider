cider.namespace('cider.index');

cider.index.updateSessionName = function(value) {
    if(value !== '') {
        preferencesObj.set('sname', value);
    } else {
        preferencesObj.remove('sname');
    }
};

cider.index.initSessionName = function() {
    var tmp = preferencesObj.get('sname');
    if(tmp) {
        $('#sname').val(tmp);
    }
};

var preferencesObj = new cider.Preferences();

$(function() {
    cider.index.initSessionName();
});