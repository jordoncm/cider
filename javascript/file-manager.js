function createFile() {
    var name = document.getElementById('name').value;
    
    var parameter = '';
    if(path != '') {
        parameter = path + '/' + name;
    } else {
        parameter = name;
    }
    
    if(name != '') {
        window.open(
            'editor.py?file=' + encodeURIComponent(parameter),
            '_blank'
        );
    }
}