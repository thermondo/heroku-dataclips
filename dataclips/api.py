# -*- coding: utf-8 -*-
from __future__ import (
    unicode_literals, absolute_import
)

import json

import requests
import slumber
from cached_property import cached_property
from lxml import html


class Client(object):
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self._headers = {'Accept': 'application/json'}
        self._base_url = 'https://dataclips.heroku.com/api/v1/'
        self._api = None
        self._sso_session = None

    def authenticate(self):
        session = requests.Session()
        res = session.get('https://id.heroku.com/login')
        assert res.status_code == 200
        tree = html.fromstring(res.content)

        data = {
            '_csrf': tree.xpath('//input[@name="_csrf"]/@value')[0],
            'email': self.email,
            'password': self.password,
            'commit': 'Log In'
        }

        res = session.post('https://id.heroku.com/login', data=data)
        assert res.status_code == 200

        # calling dataclips.heroku.com is to get the dataclips-sso-session
        res = session.get('https://dataclips.heroku.com')
        assert res.status_code == 200
        
        return session.cookies.get('dataclips-sso-session')

    @cached_property
    def api(self):
        if self._sso_session is None:
            self._sso_session = self.authenticate()

        if self._api is not None:
            return self._api

        self._session = requests.Session()
        self._session.cookies = requests.utils.cookiejar_from_dict({
            'dataclips-sso-session': self._sso_session
        })
        self._session.headers.update(self._headers)
        self._api = slumber.API(
            self._base_url,
            session=self._session,
            append_slash=False
        )
        return self._api

    def get_all_dataclips(self):
        return self.api.clips.get()

    def get_dataclip_versions(self, slug):
        return self.api.clips(slug).versions.get()

    def get_latest_dataclip(self, slug):
        for version in self.get_dataclip_versions(slug):
            if version['latest']:
                return version

    def get_recoverable_dataclips(self):
        return self.api.clips.recoverable.get()

    def get_heroku_resources(self):
        # for some reason this is coming as bytes
        resources = self.api.heroku_resources.get().decode()
        return json.loads(resources)

    def move_to_resource(self, slug, resource_id):
        post_data = {
            "heroku_resource_id": resource_id
        }
        return self.api.clips(slug).move.post(post_data)
