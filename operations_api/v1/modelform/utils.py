import crypt
import io
import json
import logging
import re
import requests
import uuid
import yaml

from flask import current_app as app

from base64 import b64encode
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from docutils.core import publish_parts
from ipaddress import IPv4Network
from jinja2 import Environment, meta
from pygerrit.rest import GerritRestAPI
from requests import HTTPError
from requests.auth import HTTPBasicAuth
from os import urandom

from operations_api import exceptions
from operations_api.app import cache

log = logging.getLogger('operations_api')


####################################
# GET CONTEXT FROM REMOTE LOCATION #
####################################

# Custom Jinja2 filters

def subnet(subnet, host_ip):
    """
    Create network object and get host by index

    Example:

        Context
        -------
        {'my_subnet': '192.168.1.0/24'}

        Template
        --------
        {{ my_subnet|subnet(1) }}

        Output
        ------
        192.168.1.1
    """
    if not subnet:
        return ""

    if '/' not in subnet:
        subnet = str(subnet) + '/24'

    try:
        network = IPv4Network(str(subnet))
        idx = int(host_ip) - 1
        ipaddr = str(list(network.hosts())[idx])
    except IndexError:
        ipaddr = "Host index is out of range of available addresses"
    except:
        ipaddr = subnet.split('/')[0]

    return ipaddr


def netmask(subnet):
    """
    Create network object and get netmask

    Example:

        Context
        -------
        {'my_subnet': '192.168.1.0/24'}

        Template
        --------
        {{ my_subnet|netmask }}

        Output
        ------
        255.255.255.0
    """
    if not subnet:
        return ""

    if '/' not in subnet:
        subnet = str(subnet) + '/24'

    try:
        network = IPv4Network(str(subnet))
        netmask = str(network.netmask)
    except:
        netmask = "Cannot determine network mask"

    return netmask


def generate_password(length):
    """
    Generate password of defined length

    Example:

        Template
        --------
        {{ 32|generate_password }}

        Output
        ------
        Jda0HK9rM4UETFzZllDPbu8i2szzKbMM
    """
    chars = "aAbBcCdDeEfFgGhHiIjJkKlLmMnNpPqQrRsStTuUvVwWxXyYzZ1234567890"

    return "".join(chars[ord(c) % len(chars)] for c in b64encode(urandom(length)).decode('utf-8'))


def hash_password(password):
    """
    Hash password

    Example:

        Context
        -------
        {'some_password': 'Jda0HK9rM4UETFzZllDPbu8i2szzKbMM'}

        Template
        --------
        {{ some_password|hash_password }}

        Output
        ------
        $2b$12$HXXew12E9mN3NIXv/egSDurU.dshYQRepBoeY.6bfbOOS5IyFVIBa
    """
    chars = "aAbBcCdDeEfFgGhHiIjJkKlLmMnNpPqQrRsStTuUvVwWxXyYzZ"
    salt_str = "".join(chars[ord(c) % len(chars)] for c in b64encode(urandom(8)).decode('utf-8'))
    salt = "$6$%s$" % salt_str
    pw_hash = ''
    if password:
        pw_hash = crypt.crypt(password, salt)

    return pw_hash


CUSTOM_FILTERS = [
    ('subnet', subnet),
    ('generate_password', generate_password),
    ('hash_password', hash_password),
    ('netmask', netmask)
]


def generate_ssh_keypair(seed=None):
    if not seed:
        private_key_str = ""
        public_key_str = ""
    else:
        private_key_cache = 'private_key_' + str(seed)
        public_key_cache = 'public_key_' + str(seed)
        cached_private_key = cache.get(private_key_cache)
        cached_public_key = cache.get(public_key_cache)

        if cached_private_key and cached_public_key:
            private_key_str = cached_private_key
            public_key_str = cached_public_key

        else:
            private_key_obj = rsa.generate_private_key(
                backend=default_backend(),
                public_exponent=65537,
                key_size=2048
            )

            public_key_obj = private_key_obj.public_key()

            public_key = public_key_obj.public_bytes(
                serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH)

            private_key = private_key_obj.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption())

            private_key_str = private_key.decode('utf-8')
            public_key_str = public_key.decode('utf-8')

            cache.set(private_key_cache, private_key_str, 3600)
            cache.set(public_key_cache, public_key_str, 3600)

    return (private_key_str, public_key_str)


def generate_uuid():
    return uuid.uuid4()


CUSTOM_FUNCTIONS = [
    ('generate_ssh_keypair', generate_ssh_keypair),
    ('generate_uuid', generate_uuid)
]

DOCUTILS_RENDERER_SETTINGS = {
    'initial_header_level': 2,
    # important, to have even lone titles stay in the html fragment:
    'doctitle_xform': False,
    # we also disable the promotion of lone subsection title to a subtitle:
    'sectsubtitle_xform': False,
    'file_insertion_enabled': False,  # SECURITY MEASURE (file hacking)
    'raw_enabled': False,             # SECURITY MEASURE (script tag)
    'report_level': 2,                # report warnings and above, by default
}


# Decorators

def requires(attributes):
    # check if required attributes are present on object
    # instance and have assigned values
    # attributes: [string, ...]
    def wrap(f):
        def wrapped_f(self, *args):
            for attr in attributes:
                if not getattr(self, attr):
                    msg = ('Configuration key MODELFORM_{} is '
                           'required with remote {}').format(attr.upper(), self.remote)
                    raise exceptions.ImproperlyConfigured(msg)
            return f(self, *args)
        return wrapped_f
    return wrap


# Template Collector

class FormTemplateCollector(object):
    '''
    TODO: document this class
    '''

    def __init__(self, *args, **kwargs):
        self.url = kwargs.get('url', app.config.get('MODELFORM_URL', None))
        self.path = kwargs.get('path', app.config.get('MODELFORM_PATH', None))
        self.remote = kwargs.get('remote', app.config.get('MODELFORM_REMOTE', None))
        self.username = kwargs.get('username', app.config.get('MODELFORM_USERNAME', None))
        self.password = kwargs.get('password', app.config.get('MODELFORM_PASSWORD', None))
        self.token = kwargs.get('token', app.config.get('MODELFORM_TOKEN', None))
        self.versions = kwargs.get('versions', app.config.get('MODELFORM_VERSIONS', []))
        self.project_name = kwargs.get('project_name', app.config.get('MODELFORM_PROJECT_NAME', None))
        self.file_name = kwargs.get('file_name', app.config.get('MODELFORM_FILE_NAME', None))
        self.version_filter = kwargs.get('version_filter', app.config.get('MODELFORM_VERSION_FILTER', None))
        self.version_map = kwargs.get('version_map', app.config.get('MODELFORM_VERSION_MAP', {}))
        self.collectors = {
            'github': {
                'template_collector': self._github_collector,
                'version_collector': self._static_version_collector
            },
            'http': {
                'template_collector': self._http_collector,
                'version_collector': self._static_version_collector
            },
            'gerrit': {
                'template_collector': self._gerrit_collector,
                'version_collector': self._gerrit_version_collector
            },
            'localfs': {
                'template_collector': self._localfs_collector,
                'version_collector': self._static_version_collector
            }
        }
        if not self.remote or (self.remote and self.remote not in self.collectors):
            collectors = list(self.collectors.keys())
            msg = ('Configuration key MODELFORM_REMOTE is '
                   'required, possible values are: {}').format(', '.join(collectors))
            raise exceptions.ImproperlyConfigured(msg)

    # GERRIT
    def _gerrit_get(self, endpoint_url):
        auth = HTTPBasicAuth(self.username, self.password)
        rest = GerritRestAPI(url=self.url, auth=auth)
        response_body = ''
        try:
            response_body = rest.get(endpoint_url)
        except HTTPError as e:
            msg = "Failed to get response from Gerrit URL %s: %s" % (endpoint_url, str(e))
            log.error(msg)
        except Exception as e:
            log.exception(e)
        return response_body

    @requires(['username', 'password', 'url', 'project_name', 'file_name'])
    def _gerrit_collector(self, version=None):
        cache_key = 'workflow_context'
        endpoint_url = '/projects/%s/branches/master/files/%s/content' % (self.project_name, self.file_name)
        if version:
            versions = self._gerrit_get_versions()
            if version in self.version_map.values():
                version = [v[0] for v in self.version_map.items() if v[1] == version][0]
            revision = versions.get(version)
            cache_key = 'workflow_context_%s' % revision
            endpoint_url = '/projects/%s/commits/%s/files/%s/content' % (
                self.project_name, revision, self.file_name)

        cached_ctx = cache.get(cache_key)
        if cached_ctx:
            return cached_ctx

        ctx = self._gerrit_get(endpoint_url)
        cache.set(cache_key, ctx, 3600)
        return ctx

    def _gerrit_get_versions(self):
        cache_key = 'workflow_versions_%s_%s' % (self.url, self.project_name)
        cached_versions = cache.get(cache_key)
        if cached_versions:
            return cached_versions

        tags_endpoint_url = '/projects/%s/tags/' % self.project_name
        master_endpoint_url = '/projects/%s/branches/master/' % self.project_name

        tags = self._gerrit_get(tags_endpoint_url)
        master = self._gerrit_get(master_endpoint_url)

        self.versions = {}
        for tag in tags:
            key = tag['ref'].replace('refs/tags/', '')
            self.versions[key] = tag['revision']
        self.versions['master'] = master['revision']

        cache.set(cache_key, self.versions, 3600)
        return self.versions

    def _gerrit_version_collector(self):
        versions = self._gerrit_get_versions()
        return list(versions.keys())

    # GITHUB
    @requires(['url', 'token'])
    def _github_collector(self, version=None):
        session = requests.Session()

        cached_ctx = cache.get('workflow_context')
        if cached_ctx:
            return cached_ctx

        session.headers.update({'Accept': 'application/vnd.github.v3.raw'})
        session.headers.update({'Authorization': 'token ' + str(self.token)})
        response = session.get(self.url)
        if response.status_code >= 300:
            try:
                response_json = json.loads(str(response.text))
                response_text = response_json['message']
            except:
                response_text = response.text
            msg = "Could not get remote file from Github:\nSTATUS CODE: %s\nRESPONSE:\n%s" % (
                str(response.status_code), response_text)
            log.error(msg)
            ctx = ""
        else:
            ctx = response.text

        cache.set('workflow_context', ctx, 3600)

        return ctx

    # HTTP
    @requires(['url'])
    def _http_collector(self, version=None):
        session = requests.Session()

        cached_ctx = cache.get('workflow_context')
        if cached_ctx:
            return cached_ctx

        if self.username and self.password:
            response = session.get(self.url, auth=(self.username, self.password))
        else:
            response = session.get(self.url)

        if response.status_code >= 300:
            msg = "Could not get remote file from HTTP URL %s:\nSTATUS CODE: %s\nRESPONSE:\n%s" % (
                self.url, str(response.status_code), response.text)
            log.error(msg)
            ctx = ""
        else:
            ctx = response.text

        cache.set('workflow_context', ctx, 3600)

        return ctx

    # LOCALFS
    @requires(['path'])
    def _localfs_collector(self, version=None):
        try:
            with io.open(self.path, 'r') as file_handle:
                ctx = file_handle.read()
        except Exception as e:
            msg = "Could not read file %s: %s" % (self.path, repr(e))
            log.error(msg)
            ctx = ""

        return ctx

    def _static_version_collector(self):
        return self.versions

    # PRIVATE
    def _collect_template(self, version=None):
        if version:
            versions = self.list_versions()
            if version not in versions:
                log.warning('Selected version %s not available, using default. Available versions: %s' % (
                    version, versions))
                version = None

        collector = self.collectors.get(self.remote, {}).get('template_collector')
        return collector(version)

    def _render_doc(self, value, header_level=None, report_level=None):
        settings_overrides = DOCUTILS_RENDERER_SETTINGS.copy()
        if header_level is not None:  # starts from 1
            settings_overrides["initial_header_level"] = header_level
        if report_level is not None:  # starts from 1 too
            settings_overrides["report_level"] = report_level
        parts = publish_parts(source=value.encode('utf-8'),
                              writer_name="html4css1",
                              settings_overrides=settings_overrides)
        trimmed_parts = parts['html_body'][23:-8]
        return trimmed_parts.decode('utf-8')

    # PUBLIC
    def list_versions(self):
        collector = self.collectors.get(self.remote, {}).get('version_collector')
        versions = collector()

        # filter versions by configured regular expression
        if self.version_filter:
            regex = re.compile(self.version_filter)
            versions = list(filter(regex.search, versions))

        # replace version names by names configured in version map
        for idx, version in enumerate(versions):
            if version in self.version_map:
                versions[idx] = self.version_map[version]

        return sorted(versions)

    def render(self, version=None):
        context = {}
        env = Environment()
        for fltr in CUSTOM_FILTERS:
            env.filters[fltr[0]] = fltr[1]
        for fnc in CUSTOM_FUNCTIONS:
            env.globals[fnc[0]] = fnc[1]
        source_context = self._collect_template(version)

        tmpl = env.from_string(source_context)
        parsed_source = env.parse(source_context)

        for key in meta.find_undeclared_variables(parsed_source):
            if key not in env.globals:
                context[key] = ''

        try:
            rendered = yaml.load(tmpl.render(context))
        except Exception as e:
            rendered = {}
            log.exception(e)

        return rendered
