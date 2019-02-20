import os
import requests
from notebook.base.handlers import IPythonHandler



class GetHandler(IPythonHandler):
    def get(self):

        host = os.environ.get('KUBERNETES_SERVICE_HOST')
        host_port = os.environ.get('KUBERNETES_PORT_443_TCP_PORT')
        workspace_id = os.environ.get('CHE_WORKSPACE_ID')

        with open ("/var/run/secrets/kubernetes.io/serviceaccount/token", "r") as t:
            token=t.read()

        headers = {
            'Authorization': 'Bearer ' + token,
        }

        request_string = 'https://' + host + ':' + host_port + '/api/v1/namespaces/' + workspace_id + '/services/ws'
        response = requests.get(request_string, headers=headers, verify=False)

        data = response.json()
        port = data['spec']['ports'][0]['nodePort']

        self.finish({'url': "example_url", 'port': port})
        return


