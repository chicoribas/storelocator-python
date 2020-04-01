from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import UniqueConstraint
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
import dotenv
import os


Base = declarative_base()


class Store(Base):
    __tablename__ = 'stores'

    id              = Column(Integer, primary_key=True)
    id_omnichat     = Column(String(20))
    active          = Column(Boolean)
    name            = Column(String(50))
    address         = Column(String(200))
    neighborhood    = Column(String(50))
    city            = Column(String(50))
    state           = Column(String(50))
    cep             = Column(String(9))
    created_at      = Column(DateTime, server_default=func.now())
    updated_at      = Column(DateTime, server_default=func.now())

    cache_requests = relationship("CacheRequests", back_populates="store", cascade="all, delete, delete-orphan")

    def __repr__(self):
        return "<Store(id={}, name={}, bairro={})".format(self.id, self.name, self.neighborhood)

    def to_json(self):
        return {
            "id": self.id,
            "id_omnichat": self.id_omnichat,
            "active": self.active,
            "name": self.name,
            "address": self.address,
            "neighborhood": self.neighborhood,
            "city": self.city,
            "state": self.state,
            "cep": self.cep,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

class CacheRequests(Base):
    __tablename__ = 'cache_requests'

    client_cep              = Column(String(9))
    client_address          = Column(String(200))
    client_neighborhood     = Column(String(50))
    client_city             = Column(String(50))
    client_state            = Column(String(50))
    store_id                = Column(Integer, ForeignKey('stores.id'))
    distance                = Column(Integer)
    created_at              = Column(DateTime, server_default=func.now())
    updated_at              = Column(DateTime, server_default=func.now())

    __table_args__ = (PrimaryKeyConstraint('client_cep', 'store_id'),
                      UniqueConstraint('client_cep', 'store_id'),
                      {})

    store = relationship("Store", back_populates='cache_requests')
    closest_store = relationship("CacheClosestStore", back_populates='request', cascade="all, delete, delete-orphan")

    def __repr__(self):
        return "<CacheRequest(client_cep={}, store_id={}, distance={})".format(self.client_cep,
                                                                                self.store_id,
                                                                                self.distance)

    def to_json(self):
        return {
            "client_cep": self.client_cep,
            "client_address": self.client_address,
            "client_neighborhood": self.client_neighborhood,
            "client_city": self.client_city,
            "client_state": self.client_state,
            "store_id": self.store_id,
            "distance": self.distance,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class CacheClosestStore(Base):
    __tablename__ = 'cache_closest_store'

    client_cep              = Column(String(9), primary_key=True, unique=True)
    store_id                = Column(Integer)
    created_at              = Column(DateTime, server_default=func.now())
    updated_at              = Column(DateTime, server_default=func.now())

    __table_args__ = (ForeignKeyConstraint([client_cep, store_id], [CacheRequests.client_cep, CacheRequests.store_id]), {})
    request = relationship("CacheRequests", back_populates='closest_store', foreign_keys=[client_cep, store_id])

    def __repr__(self):
        return "<CacheClosestStore(client_cep={}, store_id={})".format(self.client_cep, self.store_id)


def sessionFactory():
    dotenv.load_dotenv('./.env')

    USER        = os.getenv("OMNICHAT_USER")
    PSWD        = os.getenv("OMNICHAT_PSWD")
    HOST        = os.getenv("OMNICHAT_HOST")
    DB          = os.getenv("OMNICHAT_DB")
    CERT_PARAM  = os.getenv("OMNICHAT_CERT_PARAM")
    CERT        = os.getenv("OMNICHAT_CERT")
    DIALECT     = os.getenv("OMNICHAT_DIALECT")

    ssl_args = {CERT_PARAM:CERT} if CERT_PARAM is not None else {}

    engine = create_engine(f'{DIALECT}://{USER}:{PSWD}@{HOST}/{DB}', connect_args=ssl_args)

    Base.metadata.create_all(engine)

    return sessionmaker(bind=engine)

if __name__ == "__main__":
    Session = sessionFactory()

    print('Inserir Lojas teste')

    # testing
    session = Session()
    session.add_all([
        Store(id='2852', active=True, name='AEROFARMA PERFUMARIAS LTDA', address='RODOVIA BR-277 CURITIBA-PARANAGUA, 944 - JARDIM DAS AMERICAS, CURITIBA - PR', neighborhood='JARDIM DAS AMERICAS', city='CURITIBA', state='PR', cep='81530-245'),
        Store(id='8558', active=True, name='AEROFARMA PERFUMARIAS LTDA', address='AV MAL FLORIANO PEIXOTO, 4984 - HAUER, CURITIBA - PR', neighborhood='HAUER', city='CURITIBA', state='PR', cep='81630-000'),
        Store(id='19860', active=True, name='MARANATHA PERFUMARIA E COSMETICOS', address='RUA NICOLA PELLANDA, 1346 - PINHEIRINHO, CURITIBA - PR', neighborhood='PINHEIRINHO', city='CURITIBA', state='PR', cep='81880-000'),
        Store(id='981', active=True, name='AEROFARMA PERFUMARIAS LTDA', address='AV PREF ERASTO GAERTNER, 277 - BACACHERI, CURITIBA - PR', neighborhood='BACACHERI', city='CURITIBA', state='PR', cep='82510-160'),
        Store(id='2204', active=True, name='AEROFARMA PERFUMARIAS LTDA', address='AV. MAL. FLORIANO PEIXOTO, 5895 - HAUER, CURITIBA - PR', neighborhood='HAUER', city='CURITIBA', state='PR', cep='81610-000'),
        Store(id="13169", active=True, name="INTERBELLE COMERCIO DE PRODUTOS", address="AV PRES KENNEDY, 4121 - PORTAO, CURITIBA - PR", neighborhood="PORTAO", city="CURITIBA", state="PR", cep="80610-905")
    ])
    session.commit()

