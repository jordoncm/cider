$(function() {
    var Router = Backbone.Router.extend({
        routes: {
            '*splat': 'index'
        },
        index: function() {
            $('body').append(new cider.views.TopNav().render({
                header: '',
                sub_header: '',
                sub_header_link: '',
                extra: ''
            }).$el);
            $('body').append(
                new cider.views.index.Content().render(config).$el
            );
            $('body').append(new cider.views.BottomNav().render({
                right_content: new cider.views.index.BottomNavRight().render().$el.html()
            }).$el);
        }
    });
    router = new Router();
    Backbone.history.start();
});
