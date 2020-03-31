import requests
import pycep_correios


class AddressApi:
    def __init__(self, apikey, debug=False):
        self.apikey = apikey
        self.debug = debug

    @staticmethod
    def get_address_from_cep(cep):
        mapping = {
            'bairro': 'neighborhood',
            'cep': 'cep',
            'cidade': 'city',
            'logradouro': 'street',
            'uf': 'state',
            'complemento': 'complement'
        }
        return {mapping.get(k, k):v for k,v in pycep_correios.get_address_from_cep(cep).items()}

    def get_distance(self, origin, destination):
        if self.debug: print(f"Buscando distância entre {origin} e {destination}")
        apikey = self.apikey
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={origin}&destinations={destination}&key={apikey}"

        payload = {}
        headers= {}

        response = requests.request("GET", url, headers=headers, data = payload)
        response = response.json()

        return response['rows'][0]['elements'][0]['distance']['value']
