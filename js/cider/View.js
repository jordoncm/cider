cider.namespace('cider');

cider.View = cider.extend();

cider.View.prototype.templateCode = '';

cider.View.prototype.template = null;

cider.View.prototype.init = function(config) {
    this.template = _.template(this.templateCode);
};

cider.View.prototype.render = function(data) {
    if(data) {
        return this.template(data);
    } else {
        return this.template();
    }
};