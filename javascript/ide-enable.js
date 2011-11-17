var ide = {
    openFile : function(file) {
        try {
            window.parent.addTab(file);
            
            return false;
        } catch(e) {
            return true;
        }
    },
    closeFile : function(file) {
        try {
            window.parent.removeTab(file);
            
            return false;
        } catch(e) {
            window.close();
            return true;
        }
    }
};