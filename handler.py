import dotenv; dotenv.load_dotenv('./.env')
from storefinder import StoreFinder

import json

# serverless invoke local --function hello --path data.json -e OMNICHAT_USER="ibm_cloud_61375270_374b_42e6_8931_d89e15003c0b" -e OMNICHAT_PSWD="6593367995bdb37710e12c15603dc100f29fd31a11d63f00fddf00f5a8ac81f9" -e OMNICHAT_HOST="f38d54b3-edbf-4554-a43d-8126aa3c418d.blrrvkdw0thh68l98t20.databases.appdomain.cloud:31110" -e OMNICHAT_DB="ibmclouddb" -e OMNICHAT_CERT_PARAM='sslrootcert' -e OMNICHAT_CERT="db.cert" -e OMNICHAT_DIALECT="postgresql" -e GMAPS_API_KEY="AIzaSyCDr-67_8-I958h-l_pfqT9BXV_ZUnPhsQ"

def hello(event, context):
    
    print(event)

    cep=event['queryStringParameters']['cep']

    store_finder=StoreFinder(debug=True)

    store=store_finder.get_closest_store(cep).to_json()
    
    print("Fim execução")

    result = {'statusCode': 200,
            'body': json.dumps(dict(store))}

    print(result)

    return result

