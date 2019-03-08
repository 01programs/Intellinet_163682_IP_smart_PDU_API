#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
"""Summary
"""
import requests
from lxml import etree as et
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlunsplit





""" WARNING - WARNING - WARNING - WARNING - WARNING - WARNING - WARNING

        I STRONGLY DISCOURAGE YOU FROM USING THIS PDU IN PRODUCTION. 
        IT'S SECURITY IS VIRTUALLY NON EXISTENT AND I FOUND MULTIPLE 
        EXPLOITABLE VULNERABILITIES JUST WHILE WRITING THIS API WRAPPER 

    WARNING - WARNING - WARNING - WARNING - WARNING - WARNING - WARNING """







class IPU():

    """This class is represents a api wrapper for the Intellinet IP smart PDU API [163682].
        It provides all the functionality of the web interface it is based on.
    
    Class-Attributes:
        DEFAULT_CREDS (:obj:`tuple` of :obj:`str`): default username/password of pdu
        DEFAULT_ENDCODING (str): default encoding of pdu
        DEFAULT_SCHEMA (str): default schema of pdu
    """
    
    DEFAULT_SCHEMA = "http"
    DEFAULT_ENDCODING = "gb2312"
    DEFAULT_CREDS = ("admin", "admin")

    def __init__(self, host, auth=None, charset=None, schema=None):
        """        
        Args:
            host (str): IP addr of pdu/ipu
            auth (:obj:`tuple` of :obj:`str`, optional): (username, password). Defaults to DEFAULT_CREDS
            charset (str): charset used by the pdu. Defaults to DEFAULT_ENDCODING
            schema (str, optional): 'http' or 'https'. Defaults to DEFAULT_SCHEMA
        """
        self.host = host
        self.schema = schema or self.DEFAULT_SCHEMA
        self.charset = charset or self.DEFAULT_ENDCODING
        self.credentials = auth or self.DEFAULT_CREDS
        self.auth = self._auth(self.credentials)
        self.endpoints = {
        # Information
        "status": "status.xml",
        "pdu": "info_PDU.htm",
        "system": "info_system.htm",
        # Control
        "outlet": "control_outlet.htm",
        # Config
        "config_pdu": "config_PDU.htm",
        "thresholds": "config_threshold.htm",
        "users": "config_user.htm",
        "network": "config_network.htm",
        }


    # api helper functions

    def print_help(self):
        """ Prints all available endpoints in a quick and dirty format.
        """
        print(self.endpoints)

    def _get_request(self, page, params=None):
        """Internal wrapper around requests get method and the pdus available endpoints.
        
        Args:
            page (str): endpoint / page that is requested
            params (dict, optional): get parametrs to be send along with request. Used for updating settings.
        
        Returns:
            :obj:`requests.models.Response`: The raw object returned by the requests lib.
        """
        url = urlunsplit([self.schema, self.host, page, None, None])
        return requests.get(url, auth=self.auth, params=params)

    def _post_request(self, page, data):
        """Internal wrapper around requests post method and the pdus available endpoints.
        
        Args:
            page (str): See: self._get_request()
            data (dict): post data
        """
        url = urlunsplit([self.schema, self.host, page, None, None])

        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        return requests.post(url, auth=self.auth, data=data, headers=headers)

    def _decode_response(self, resp):
        """simple helper to decode requests responses.
        
        Args:
            resp (:obj:`requests.models.Response`): The raw object returned by the requests lib.
        
        Returns:
            str: decoded string that was contained in the response from the api.
        """
        return resp.content.decode(self.charset)

    def _parse_resp_content(self, raw_resp_content):
        """simple wrapper around lxml that automatically uses the correct xml/html parser.
        
        Args:
            raw_resp_content (str): the decoded response from the api.
        
        Returns:
            :obj:`lxml.etree._Element`: searchable etree of the response string passed to the function.
        """
        # dynamically select parser for html and xml response absed on the key word 'html' in the resp. content.

        if 'html' in raw_resp_content.lower():
            parser = et.HTML
        else:
            parser = et.XML

        return parser(raw_resp_content)

    def _api_request(self, page, params=None, data=None):
        """One strop shop helper for api requests. Hightes level wrapper which requests, decodes and parses in one step.
        
        Args:
            page (str): endpoint to be used
            params (dict, optional): optional get parameters to be send along with the request.
            data (dict, optional): will cause the api call to be performed as HTTP POST request with `data` as payload. 
                In this case `params` will be ignored.
        Returns:
            :obj:`lxml.etree._Element`: See: self._parse_resp_content
        """

        if data:
            resp = self._post_request(page, data=data)
        else:
            resp = self._get_request(page, params=params)
        return self._parse_resp_content(self._decode_response(resp))


    def _auth(self, creds):
        """Don't even bother... The PDU only requests a http auth on the / page. 
            All other pages/endpoints (including settings updates und file uploads)
            are unprotected.
        
        Args:
            creds (:obj:`tuple` of :obj:`str`): (username, password).
        
        Returns:
            :obj:`requests.auth.HTTPBasicAuth`: requestes auth class.
        """
        return requests.auth.HTTPBasicAuth(*creds)


    def _extract_value(self, etree, xml_element_name):
        """simple weapper around lxml value extration.
        
        Args:
            etree (:obj:`lxml.etree._Element`): a lxml etree
            xml_element_name (str): the name of the values coresponding element. 
        
        Returns:
            str: the value belonging to `xml_element_name`
        """
        return etree.find(xml_element_name).text


    # public api

    def status(self):
        """gives you basic status/health of the device. 
            Values: deg. C, outlet states [on/off], status [read: are there warnings?], humidity in perc, amps.
        Returns:
            dict: containing the aforementioned stats. 
                  e.g. {'degree_celcius': '26', 'outlet_states': ['on', 'on', 'off', 'on', 'on', 'on', 'on', 'on'],
                        'stat': 'normal', 'humidity_percent': '27', 'current_amperes': '0.5'}
        """
        endpoint = self.endpoints["status"]
        e = self._api_request(endpoint)
        return {
            "current_amperes": self._extract_value(e, "cur0"),
            "degree_celcius": self._extract_value(e, "tempBan"),
            "humidity_percent": self._extract_value(e, "humBan"),
            "stat": self._extract_value(e, "stat0"),
            "outlet_states": [self._extract_value(e, "outletStat{}".format(i)) for i in range(0,8)]
        }

    def pdu_config(self, outlet_configs=None):
        """ Getter/setter for outlet configs. 
            Allows you to name the outlets as well as set turn on/off delays 
            to prevent overloading or create boot/shutdown orders.
        
        Args:
            outlet_configs (dict, optional): if present the pdu config will be updates to fit the given dict. Format:
                {'outlet1': {'outlet_name': 'outlet3', 'turn_on_delay': 3, 'turn_of_delay': 3},
                'outlet2': ... }
        
        Returns:
            :obj:`dict` of :obj:`dict` or None: Keys: `turn_on_delay`, `turn_off_delay`, `name`
        """
        if outlet_configs:
            self._set_config_pdu(outlet_configs)

        return self._get_config_pdu()

    def _set_config_pdu(self, outlet_configs):
        """Setter for self.pdu_config()
        
        Args:
            outlet_configs (dict): dict that is formatted like the output of self._get_config_pdu()
        """
        endpoint = self.endpoints['config_pdu']

        translation_table = {'turn_on_delay': 'ondly', 'turn_off_delay': 'ofdly', 'name': 'otlt'}

        settings = {}
        for k, v in outlet_configs.items():
            otl_nr = k.replace('outlet', '')

            for _k, _v in v.items():
                new_key = translation_table[_k] + otl_nr
                settings[new_key] = _v

        etree = self._api_request(endpoint, data=settings)

    def _get_config_pdu(self):
        """Getter for self.pdu_config()
        
        Returns:
            :obj:`dict` of :obj:`dict`: e.g.
            {
                'outlet5': {'turn_on_delay': 9, 'turn_off_delay': 9, 'name': 'GINA'}, 
                'outlet2': {'turn_on_delay': 6, 'turn_off_delay': 6, 'name': 'Steckdose2'},
                'outlet7': {'turn_on_delay': 11, 'turn_off_delay': 11, 'name': 'Steckdose7'},
                'outlet1': {'turn_on_delay': 5, 'turn_off_delay': 5, 'name': 'PACS'},
                'outlet6': {'turn_on_delay': 10, 'turn_off_delay': 10, 'name': 'GINA Router'},
                'outlet3': {'turn_on_delay': 7, 'turn_off_delay': 7, 'name': 'Steckdose3'},
                'outlet8': {'turn_on_delay': 12, 'turn_off_delay': 12, 'name': 'UPC Modem'},
                'outlet4': {'turn_on_delay': 8, 'turn_off_delay': 8, 'name': 'Steckdose4'}
            }
        """
        endpoint = self.endpoints['config_pdu']
        etree = self._api_request(endpoint)
        xpath_input_field_values = './/td/input/@value' # get the value of the value attribute in the input tag which is within a td tag
        xpath_input_fields = './/tr[td/input/@value]' # get every tr tag which has at least one td tag which has at least one input tag with a value attribute

        config = {}
        for idx, outlet in enumerate(etree.xpath(xpath_input_fields)):
            values = outlet.xpath(xpath_input_field_values)
            config['outlet{}'.format(idx)] = {
                'name': values[0],
                'turn_on_delay': int(values[1]),
                'turn_off_delay': int(values[2])
                }

        return config

    def control_outlets(self, list_of_outlet_ids=None, state=None):
        list_of_outlet_ids = list_of_outlet_ids or [i for i in range(0, 8)]

        if state:
            return self._set_outlet_states(self, list_of_outlet_ids, state)

        return self._get_outlet_states(self, list_of_outlet_ids)


    def _get_outlet_states(self, list_of_outlet_ids):
        """wrapper around self.status() returns only on/off for the given outlet_ids.
        
        Args:
            list_of_outlet_ids (:obj:`list` of `int`): the ids of the outlets you want see.
        
        Returns:
            :obj:`list` of `str`: e.g. ['on', 'off', 'off', 'off', 'on']
        """
        status = self.status()
        return list(status['outlet_states'][i] for i in list_of_outlet_ids)

    def _set_outlet_states(self, list_of_outlet_ids, state):
        """A `list_of_outlet_ids` will be set to a given `state`.
        
        Args:
            list_of_outlet_ids (:obj:`list` of `int`): the ids of the outlets you want to change.
            state (str): One of ['on', 'off', 'power_cycle_off_on']
        
        Returns:
            :obj:`lxml.etree._Element`: the api response
        """

        endpoint = self.endpoints['outlet']
        translation_table = {'on': 0, 'off': 1, 'power_cycle_off_on': 2}
        outlet_states = {'outlet{}'.format(k):1 for k in list_of_outlet_ids}
        outlet_states['op'] = translation_table[state]
        outlet_states['submit'] = 'Anwenden'
        return self._api_request(endpoint, params=outlet_states)

    def enable_outlets(self, list_of_outlet_ids):
        """Wrapper around self._set_outlet_states() to enable all given outlets
        
        Args:
            list_of_outlet_ids (:obj:`list` of `int`): See: self._set_outlet_states()
        
        Returns:
            :obj:`lxml.etree._Element`: See: self._set_outlet_states()
        """
        return self._set_outlet_states(list_of_outlet_ids, 'on')

    def disable_outlets(self, list_of_outlet_ids):
        """Wrapper around self._set_outlet_states() to disable all given outlets
        
        Args:
            list_of_outlet_ids (:obj:`list` of `int`): See: self._set_outlet_states()
        
        Returns:
            :obj:`lxml.etree._Element`: See: self._set_outlet_states()
        """
        return self._set_outlet_states(list_of_outlet_ids, 'off')

    def power_cycle_outlets(self, list_of_outlet_ids):
        """Wrapper around self._set_outlet_states() to perform a power cycle on all given outlets
        
        Args:
            list_of_outlet_ids (:obj:`list` of `int`): See: self._set_outlet_states()
        
        Returns:
            :obj:`lxml.etree._Element`: See: self._set_outlet_states()
        """
        return self._set_outlet_states(list_of_outlet_ids, 'power_cycle_off_on')

    def outlet_names(self):
        """Simply get a list of outlet names
        
        Returns:
            list_of_outlet_ids (:obj:`tuple` of `str`): ('machine_name', 'human_name')
        """
        config = self.pdu_config()
        names = [(k, v['name']) for k,v in config.items()]
        return sorted(names, key=lambda x: x[0])

    def config_network(self):
        raise NotImplementedError

    def config_user(self):
        raise NotImplementedError

    def config_threshold(self):
        raise NotImplementedError

    def info_pdu(self):
        raise NotImplementedError

    def info_system(self):
        # this really should be called control/config_system
        raise NotImplementedError