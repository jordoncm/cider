function getCreateParameter() {
    var name = document.getElementById('name').value;
    
    var parameter = '';
    if(path != '') {
        parameter = path + '/' + name;
    } else {
        parameter = name;
    }
    
    return parameter;
}

function createFile() {
    var parameter = getCreateParameter();
    
    if(document.getElementById('name').value != '') {
        window.open(
            '../editor/?file=' + encodeURIComponent(parameter),
            '_blank'
        );
    }
}

function createFolder() {
    var parameter = getCreateParameter();
    
    if(document.getElementById('name').value != '') {
        new Ajax.Request(
            '../create-folder/',
            {
                method : 'get',
                parameters : {
                    path : parameter
                },
                onSuccess : function(response) {
                    var json = response.responseText.evalJSON();
                    if(json.success) {
                        window.location.reload();
                    } else {
                        alert('Folder creation failed.');
                    }
                }
            }
        );
    }
}