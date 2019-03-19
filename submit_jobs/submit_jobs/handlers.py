from notebook.base.handlers import IPythonHandler
import requests
import json

from .fields import getFields

class GetCapabilitiesHandler(IPythonHandler):
	def get(self):
		# submit job
		# fields = ['service', 'version','url']
		fields = getFields('getCapabilities')
		params = {}
		
		for f in fields:
			try:
				arg = self.get_argument(f.lower(), '')
				params[f] = arg
			except:
				pass

		url = 'http://geoprocessing.demo.52north.org:8080/wps/WebProcessingService'
		params['service'] = 'WPS'
		params['version'] = '2.0.0'
		params['request'] = 'GetCapabilities'

		# http://geoprocessing.demo.52north.org:8080/wps/WebProcessingService?service=WPS&version=2.0.0&request=GetCapabilities
		# url = params.pop('url',None)
		r = requests.get(
			url,
			params=params
		)
		try:
			self.finish({"status_code": r.status_code, "result": r.text})
		except:
			print('failed')
			self.finish({"status_code": r.status_code, "result": r.reason})

class ExecuteHandler(IPythonHandler):
	def post(self):
		# submit job
		fields = getFields('execute')
		params = {}
		
		for f in fields:
			try:
				arg = self.get_argument(f.lower(), '')
				params[f] = arg
			except:
				pass

		# http://geoprocessing.demo.52north.org:8080/wps/WebProcessingService?service=WPS&version=2.0.0&request=GetCapabilities
		# url = params.pop('url',None)
		url = 'http://geoprocessing.demo.52north.org:8080/wps/WebProcessingService'
		r = requests.get(
			url,
			params=params
		)
		try:
			resp = json.loads(r.text)
			self.finish({"status_code": r.status_code, "result": r.text})
		except:
			self.finish({"status_code": r.status_code, "result": r.reason})

class GetStatusHandler(IPythonHandler):
	def get(self):
		fields = getFields('getStatus')
		params = {}

		for f in fields:
			try:
				arg = self.get_argument(f.lower(), '')
				params[f] = arg
			except:
				pass

		# url = params.pop('url',None)
		url = 'http://geoprocessing.demo.52north.org:8080/wps/WebProcessingService'
		params['service'] = 'WPS'
		params['version'] = '2.0.0'
		params['request'] = 'GetStatus'
		r = requests.get(
			url,
			params=params
		)
		try:
			# resp = json.loads(r.text)
			self.finish({"status_code": r.status_code, "result": r.text})
		except:
			self.finish({"status_code": r.status_code, "result": r.reason})

class GetResultHandler(IPythonHandler):
	def get(self):
		fields = getFields('getResult')
		params = {}

		for f in fields:
			try:
				arg = self.get_argument(f.lower(), '')
				params[f] = arg
			except:
				pass

		url = params.pop('url',None)
		url = 'http://geoprocessing.demo.52north.org:8080/wps/WebProcessingService'
		params['service'] = 'WPS'
		params['version'] = '2.0.0'
		params['request'] = 'GetResult'
		r.requests.get(
			url,
			params=params
		)

class DismissHandler(IPythonHandler):
	def post(self):
		fields = getFields('getResult')
		params = {}

		for f in fields:
			try:
				arg = self.get_argument(f.lower(), '')
				params[f] = arg
			except:
				pass

		url = params.pop('url',None)
		url = 'http://geoprocessing.demo.52north.org:8080/wps/WebProcessingService'
		params['service'] = 'WPS'
		params['version'] = '2.0.0'
		params['request'] = 'Dismiss'
		r.requests.get(
			url,
			params=params
		)

class DescribeProcessHandler(IPythonHandler):
	def get(self):
		fields = getFields('describeProcess')
		params = {}

		for f in fields:
			try:
				arg = self.get_argument(f.lower(), '')
				params[f] = arg
			except:
				pass

		# url = params.pop('url',None)
		url = 'http://geoprocessing.demo.52north.org:8080/wps/WebProcessingService'
		params['service'] = 'WPS'
		params['version'] = '2.0.0'
		params['request'] = 'DescribeProcess'
		print(params)
		# params['identifier']= 'all'
		r = requests.get(
			url,
			params=params
		)
		print(r)

		try:
			# resp = json.loads(r.text)
			self.finish({"status_code": r.status_code, "result": r.text})
		except:
			self.finish({"status_code": r.status_code, "result": r.reason})