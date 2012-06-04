if(typeof cider != 'object') {
    var cider = {};
}

cider.namespace = function(ns) {
    if(ns && ns !== '') {
        var parent = cider;
        ns = ns.split('.');
        for(var i = 0; i < ns.length; i++) {
            if(i !== 0 || ns[i] != 'cider') {
                if(typeof parent[ns[i]] == 'undefined') {
                    parent[ns[i]] = {};
                }
                parent = parent[ns[i]];
            }
        }
    }
};