import requests
import xml.etree.ElementTree as et


HOST = "10.0.255.80/"



class IPU():

	DEFAULT_SCHEMA = "http://"
	DEFAULT_ENDCODING = "gb2312"
	DEFAULT_CREDS = ("admin", "admin")

	def __init__(self, host, auth=None, schema=None):
		self.host = host
		self.schema = schema or self.DEFAULT_SCHEMA
		self.charset = self.DEFAULT_ENDCODING
		self.credentials = auth or self.DEFAULT_CREDS
		self.endpoints = {
		# Information
		"status": "status.xml",
		"pdu": "info_PDU.htm",
		"system": "info_system.htm",
		"info_system": "info_system.htm",
		# Control
		"outlets": "control_outlet.htm",
		# Config
		"outlets": "config_PDU.htm",
		"thresholds": "config_threshold.htm",
		"users": "config_user.htm",
		"network": "config_network.htm",
		}

	def print_help(self):
		print(self.endpoints)

	def _get_request(self, page):
		return requests.get(
			self.schema + self.host + page,
			auth=self._auth(*self.credentials)
		)

	def _post_request(self, page):
		pass

	def _api_request(self, page):
		return self._parse_response(self._decode_response(self._get_request(page)))

	def _decode_response(self, resp):
		return resp.content.decode(self.charset)

	def _parse_response(self, resp):
		return et.fromstring(resp)

	def _auth(self, username, password):
		return requests.auth.HTTPBasicAuth("admin", "admin")

	def _extract_value(self, xml_root, xml_element_name):
		return xml_root.find(xml_element_name).text

	def _print_value(self, xml_root, xml_element_name, display_name, unit=None):
		#print(xml_element_name, display_name, unit)
		if not unit:
			unit = ""
		print(display_name + ": " + self._extract_value(xml_root, xml_element_name) + " " + unit)


	# public api

	def status(self):
		endpoint = self.endpoints["status"]
		e = self._api_request(endpoint)
		self._print_value(e, "cur0", "Strom", "Amp.")
		self._print_value(e, "tempBan", "Temperatur", "grad C.")
		self._print_value(e, "humBan", "Luftfeuchte", "%")
		self._print_value(e, "stat0", "Status")
		self._print_value(e, "outletStat0", "Steckdose 1")
		self._print_value(e, "outletStat1", "Steckdose 2")
		self._print_value(e, "outletStat2", "Steckdose 3")
		self._print_value(e, "outletStat3", "Steckdose 4")
		self._print_value(e, "outletStat4", "Steckdose 5")
		self._print_value(e, "outletStat5", "Steckdose 6")
		self._print_value(e, "outletStat6", "Steckdose 7")
		self._print_value(e, "outletStat7", "Steckdose 8")



print("Connecting to %s." % HOST)

ipu = IPU(HOST)

ipu.status()



#
# <cur0>0.3</cur0>
# <stat0>normal</stat0>
# <curBan>0.3</curBan>
# <tempBan>37</tempBan>
# <humBan>21</humBan>
# <statBan>normal</statBan>
# <outletStat0>on</outletStat0>
# <outletStat1>on</outletStat1>
# <outletStat2>on</outletStat2>
# <outletStat3>on</outletStat3>
# <outletStat4>on</outletStat4>
# <outletStat5>on</outletStat5>
# <outletStat6>on</outletStat6>
# <outletStat7>on</outletStat7>
#
# <userVerifyRes>0</userVerifyRes>