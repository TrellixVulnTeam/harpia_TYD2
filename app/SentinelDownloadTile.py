from collections import OrderedDict
from os.path import exists, join
from pathlib import Path
import datetime 

import ConnectionDB as C
import geopandas as gpd
import yaml
from geopandas_postgis import PostGIS
from sentinelsat import SentinelAPI
from sqlalchemy import create_engine


# Open yaml 
with open(Path("app/config/const.yaml"), 'r') as f:
        const = yaml.safe_load(f)

# Open Datahub parameters
data_hub = const['data_hub']
user = data_hub['user'] # user_hub
password = data_hub['password'] # password_hub

# Database parameters
harpia_db = const['harpia_db'] 
host = harpia_db['host'] # host
dbname =  harpia_db['dbname'] # database 
user_db = harpia_db['user'] # user
password_db = harpia_db['password'] # password
port = harpia_db['port'] # port

# connect to the API
api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')

tiles = ['24LVJ'] # *tiles

query_kwargs = {
        'platformname': 'Sentinel-2',
        'producttype': 'S2MSI1C', # producttype
        'cloudcoverpercentage': (0, 1), # cloudcoverpercetage (min, max)
        'date': ('20170101', '20171201')} # date: begindate enddate (ex. 'NOW-14DAYS', 'NOW')

products = OrderedDict()
for tile in tiles:
    kw = query_kwargs.copy()
    kw['tileid'] = tile 
    pp = api.query(**kw)
    products.update(pp)

# GeoPandas GeoDataFrame with the metadata of the scenes and the footprints as geometries
gdf = api.to_geodataframe(products)

# Connect to Database 
conn_str = f"postgresql://{user_db}:{password_db}@{host}:{port}/{dbname}"
engine = create_engine(conn_str)

conn_string = f"host={host} dbname={dbname} user={user_db} password={password_db} port={port}"
con = C.Connection(conn_string)

home_path = str(Path.home())
dst_folder = join(home_path, 'BRUTA_DEV') # outputfile

for i in range(0, len(gdf)):
    uuid = gdf['uuid'][i] 
    
    # File path to know if it exist
    file_name = gdf['title'][i]
    file_path = join(dst_folder, f'{file_name}.zip')

    # Check if file was downloaded anytime
    query = f"SELECT index FROM metadado_img.metadado_sentinel WHERE index = '{uuid}'" # schema table
    rs = con.run_query(query)
    metadado_is_save_db = (len(rs) == 1)

    # Selecionando a linha do geodataframe
    g = gdf[gdf['uuid'] == uuid].copy()
    
    if not exists(file_path) and not metadado_is_save_db:
        print(file_name)
        g.loc[0, 'date_download'] = datetime.datetime.now()
        api.download(uuid, directory_path=dst_folder)
        g.postgis.to_postgis(con=engine, schema='metadado_img', if_exists='append', 
                        table_name='metadado_sentinel', geometry='Polygon')
    
    elif exists(file_path) and not metadado_is_save_db:
        g.postgis.to_postgis(con=engine, schema='metadado_img', if_exists='append', 
                        table_name='metadado_sentinel', geometry='Polygon')    

# Create table in order save 
'''
DROP SCHEMA metadado_img CASCADE;
CREATE SCHEMA metadado_img;
DROP SEQUENCE metadado_sentinel_id_seq CASCADE;

CREATE SEQUENCE metadado_sentinel_id_seq;

-- GRANT USAGE ON SCHEMA metadado_img TO grp_consulta;

-- GRANT ALL ON SCHEMA metadado_img TO tmzuser;

-- Table: metadado_img.metadado_sentinel

-- DROP TABLE metadado_img.metadado_sentinel;

CREATE TABLE metadado_img.metadado_sentinel
(
    index text COLLATE pg_catalog."default",
    title text COLLATE pg_catalog."default",
    link text COLLATE pg_catalog."default",
    link_alternative text COLLATE pg_catalog."default",
    link_icon text COLLATE pg_catalog."default",
    summary text COLLATE pg_catalog."default",
    datatakesensingstart timestamp without time zone,
    beginposition timestamp without time zone,
    endposition timestamp without time zone,
    ingestiondate timestamp without time zone,
    orbitnumber bigint,
    relativeorbitnumber bigint,
    cloudcoverpercentage double precision,
    sensoroperationalmode text COLLATE pg_catalog."default",
    tileid text COLLATE pg_catalog."default",
    hv_order_tileid text COLLATE pg_catalog."default",
    format text COLLATE pg_catalog."default",
    processingbaseline text COLLATE pg_catalog."default",
    platformname text COLLATE pg_catalog."default",
    filename text COLLATE pg_catalog."default",
    instrumentname text COLLATE pg_catalog."default",
    instrumentshortname text COLLATE pg_catalog."default",
    size text COLLATE pg_catalog."default",
    s2datatakeid text COLLATE pg_catalog."default",
    producttype text COLLATE pg_catalog."default",
    platformidentifier text COLLATE pg_catalog."default",
    orbitdirection text COLLATE pg_catalog."default",
    platformserialidentifier text COLLATE pg_catalog."default",
    processinglevel text COLLATE pg_catalog."default",
    identifier text COLLATE pg_catalog."default",
    uuid text COLLATE pg_catalog."default",
    geom geometry(Polygon,4326),
    id integer NOT NULL DEFAULT nextval('metadado_sentinel_id_seq'::regclass),
    date_download timestamp without time zone,
    level1cpdiidentifier character(250) COLLATE pg_catalog."default",
    is_download boolean,
    is_processed boolean,
    file_path boolean
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE metadado_img.metadado_sentinel
    OWNER to tmzuser;

-- GRANT SELECT ON TABLE metadado_img.metadado_sentinel TO grp_consulta;

-- GRANT ALL ON TABLE metadado_img.metadado_sentinel TO tmzuser;

-- Index: idx_metadado_sentinel_geom

-- DROP INDEX metadado_img.idx_metadado_sentinel_geom;

CREATE INDEX idx_metadado_sentinel_geom
    ON metadado_img.metadado_sentinel USING gist
    (geom)
    TABLESPACE pg_default;

-- Index: idx_metadado_sentinel_index

-- DROP INDEX metadado_img.idx_metadado_sentinel_index;

CREATE INDEX idx_metadado_sentinel_index
    ON metadado_img.metadado_sentinel USING btree
    (index COLLATE pg_catalog."default", id)
    TABLESPACE pg_default;
'''