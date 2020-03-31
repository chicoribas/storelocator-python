import dotenv; dotenv.load_dotenv('./.env')
from storefinder import StoreFinder

# serverless invoke local --function hello --path data.json

def hello(event, context):
    
    print(event)

    cep = event['queryStringParameters']['cep']

    store_finder = StoreFinder(debug=True)

    print("Fim execução")

    store = store_finder.get_closest_store(cep).to_json()

    print(store)

    return store_finder.get_closest_store(cep).to_json()

