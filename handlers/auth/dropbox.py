# 
# This work is copyright 2012 Jordon Mears. All rights reserved.
# 
# This file is part of Cider.
# 
# Cider is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Cider is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Cider.  If not, see <http://www.gnu.org/licenses/>.
# 

import tornado.auth
import tornado.escape
import tornado.httpclient
import tornado.web
import urllib

import log


class Mixin(tornado.auth.OAuthMixin):
    
    _OAUTH_VERSION = '1.0'
    _OAUTH_REQUEST_TOKEN_URL = 'https://api.dropbox.com/1/oauth/request_token'
    _OAUTH_ACCESS_TOKEN_URL = 'https://api.dropbox.com/1/oauth/access_token'
    _OAUTH_AUTHORIZE_URL = 'https://api.dropbox.com/1/oauth/authorize'
    _OAUTH_NO_CALLBACKS = False
    
    def dropbox_put(
        self,
        path,
        callback,
        access_token=None,
        put_args=None,
        **args
    ):
        # Add the OAuth resource request signature if we have credentials
        url = 'https://api-content.dropbox.com/1' + path
        if access_token:
            all_args = {}
            all_args.update(args)
            method = 'PUT'
            oauth = self._oauth_request_parameters(
                url,
                access_token,
                all_args,
                method=method
            )
            args.update(oauth)
        if args:
            url += '?' + urllib.urlencode(args)
        callback = self.async_callback(self._on_dropbox_request, callback)
        http = tornado.httpclient.AsyncHTTPClient()
        http.fetch(
            url,
            method='PUT',
            body=put_args,
            callback=callback
        )
    
    def dropbox_request(
        self,
        path,
        callback,
        access_token=None,
        post_args=None,
        **args
    ):
        # Add the OAuth resource request signature if we have credentials
        pathList = path.split('/')
        pathPart = pathList[0]
        if pathPart == '' and len(pathList) > 1:
            pathPart = pathList[1]
        subdomain = 'api'
        if pathPart in ['files', 'files_put', 'thumbnails']:
            subdomain = 'api-content'
        url = 'https://' + subdomain + '.dropbox.com/1' + path
        if access_token:
            all_args = {}
            all_args.update(args)
            all_args.update(post_args or {})
            method = 'POST' if post_args is not None else 'GET'
            oauth = self._oauth_request_parameters(
                url,
                access_token,
                all_args,
                method=method
            )
            args.update(oauth)
        if args:
            url += '?' + urllib.urlencode(args)
        callback = self.async_callback(self._on_dropbox_request, callback)
        http = tornado.httpclient.AsyncHTTPClient()
        if post_args is not None:
            http.fetch(
                url,
                method='POST',
                body=urllib.urlencode(post_args),
                callback=callback
            )
        else:
            http.fetch(url, callback=callback)

    def _on_dropbox_request(self, callback, response):
        if response.error:
            log.warn(
                'Error response %s fetching %s.' % (response.error, response.request.url)
            )
            callback(None)
            return
        try:
            callback(tornado.escape.json_decode(response.body))
        except:
            callback(response.body)

    def _oauth_consumer_token(self):
        self.require_setting('dropbox_consumer_key', 'Dropbox OAuth')
        self.require_setting('dropbox_consumer_secret', 'Dropbox OAuth')
        return dict(
            key=self.settings['dropbox_consumer_key'],
            secret=self.settings['dropbox_consumer_secret']
        )

    def _oauth_get_user(self, access_token, callback):
        callback = self.async_callback(self._parse_user_response, callback)
        self.dropbox_request(
            '/account/info',
            access_token=access_token,
            callback=callback
        )

    def _parse_user_response(self, callback, user):
        if user:
            user['username'] = user['uid']
        callback(user)


class BaseAuthHandler(tornado.web.RequestHandler):
    
    def get_current_user(self):
        json = self.get_secure_cookie('user')
        if not json:
            return None
        return tornado.escape.json_decode(json)
    
    def get_login_url(self):
        return '/auth/dropbox/'


class DropboxHandler(BaseAuthHandler, Mixin):
    
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument('oauth_token', None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authorize_redirect(
            '/auth/dropbox?next=' + tornado.escape.url_escape(
                self.get_argument('next', '/')
            )
        )
    
    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, 'Dropbox auth failed.')
        self.set_secure_cookie('user', tornado.escape.json_encode(user))
        self.redirect(self.get_argument('next', '/'))