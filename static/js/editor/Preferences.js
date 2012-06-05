cider.namespace('cider.editor');

cider.editor.Preferences = function(config) {
    this.get = function(key) {
        var value = localStorage.getItem(key);
        if(value) {
            try {
                return JSON.parse(value);
            } catch(e) {
                return value;
            }
        }
        return value;
    };
    this.set = function(key, value) {
        if(typeof value == 'object') {
            localStorage.setItem(key, JSON.stringify(value));
        } else {
            localStorage.setItem(key, value);
        }
    };
    
    this.init = function(config) {};
    this.init(config);
};