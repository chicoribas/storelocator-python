from sqlalchemy import text, and_, join, Table, Column, String, Integer
from sqlalchemy.orm import contains_eager
from sqlalchemy.sql import select, func
from orm import sessionFactory
from orm import CacheClosestStore
from orm import CacheRequests
from orm import Store
from orm import Base
from addressapi import AddressApi
import os


API_KEY = os.getenv("GMAPS_API_KEY")
if API_KEY is None:
    raise Exception("GMAPS_API_KEY environment variable not set")


class StoreFinder:
    def __init__(self, debug=False):
        self.debug = debug
        self.sessionFactory = sessionFactory()
        self.address_api = AddressApi(API_KEY)

    def get_session(self):
        return self.sessionFactory()

    def get_closest_store(self, cep):
        session = self.get_session()
        get_closest_store = lambda: session.query(CacheClosestStore)\
                        .join(CacheRequests)\
                        .join(Store, and_(Store.id == CacheRequests.store_id, Store.active == True))\
                        .filter(CacheClosestStore.client_cep == cep,
                                text("""cache_closest_store.CREATED_AT > COALESCE((
                                        select
                                            max(UPDATED_AT)
                                        from
                                            stores
                                        where
                                            lower(state) = lower(cache_requests.client_state) 
                                            and lower(city) = lower(cache_requests.client_city)), '1900-01-01')"""))\
                        .first()

        closest_store = get_closest_store()

        if closest_store is None:
            if self.debug: print("Não há loja mais próxima cacheada para esse endereço.")

            client_address = AddressApi.get_address_from_cep(cep)

            search_hierarchy = [['state', 'city', 'neighborhood'],
                                ['state', 'city'],
                                ['state']]

            for h in search_hierarchy:
                print("Buscando loja no nivel {}".format(h))
                filters = [func.lower(getattr(Store, col)) == client_address[col].lower() for col in h]
                print(filters)
                stores_to_search = session.query(Store).outerjoin(CacheRequests, and_(Store.cache_requests,
                                                                                      CacheRequests.client_cep == cep))\
                                                       .filter(
                                                           Store.active == True,
                                                           CacheRequests.store_id == None,
                                                           *filters
                                                        ).all()

                if len(stores_to_search) > 0:
                    break
                else:
                    if self.debug: print("Nenhuma loja encontrada no nível {}".format(h))

            # TODO use threading
            if stores_to_search is not None:
                for store in stores_to_search:
                    # TODO API error handling
                    distance = self.address_api.get_distance(cep, store.address)

                    session.add(CacheRequests(client_cep=cep,
                                  client_address=client_address['street'],
                                  client_neighborhood=client_address['neighborhood'],
                                  client_city=client_address['city'],
                                  client_state=client_address['state'],
                                  store_id=store.id,
                                  distance=distance))
                    session.commit()

                # delete last saved closest store
                last_item = session.query(CacheClosestStore).filter(CacheClosestStore.client_cep == cep).first()
                if last_item is not None:
                    session.delete(last_item)
                    session.commit()

                session = self.get_session()

                # find new closest store
                query = select([CacheRequests.client_cep, CacheRequests.store_id]).select_from(
                    CacheRequests.__table__.join(Store.__table__, and_(Store.id == CacheRequests.store_id, Store.active == True))
                ).where(CacheRequests.client_cep == cep).order_by('distance').limit(1)
                
                cache_closest_store = CacheClosestStore.__table__
                session.execute(cache_closest_store.insert().from_select([CacheClosestStore.client_cep, CacheClosestStore.store_id], query))

                session.commit()
            
            closest_store = get_closest_store()

        return closest_store.request.store