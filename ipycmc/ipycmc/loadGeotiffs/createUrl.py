"""
This file has all the load_geotiffs helper methods that help create

Written by Grace Llewellyn
"""

from cogeo_mosaic.mosaic import MosaicJSON
from concurrent import futures
from rio_tiler.io import COGReader
import copy
from . import errorChecking
import os
import requests
import json

global required_info

def initialize_required_info(required_info_given):
    global required_info
    required_info = required_info_given

# Returns the list for a mosaic JSON for the given s3 links. Returns None in case of error and prints the appropriate error message
def create_mosaic_json_url(urls, default_ops, debug_mode):
    # TODO error check in this function and potentially return None, remember to get None in loadGeotiffs
    mosaic_data_json = create_mosaic_json(urls)
    posting_endpoint = required_info.posting_tiler_endpoint
    
    # Post the mosaic json
    r = requests.post(
        url=f"{posting_endpoint}/mosaicjson/mosaics",
        headers={
            "Content-Type": "application/vnd.titiler.mosaicjson+json",
        },
        json=mosaic_data_json).json()
        
    try:
        xml_endpoint = eval(required_info.getting_wmts_endpoint)
    except:
        print("getting_wmts_endpoint variable unable to be evaluated from variables.json or error in request url "+r)
        return None

    return add_defaults_url(xml_endpoint + "?", default_ops, debug_mode)

# Creates a variable representing a mosaic JSON to pass to the Tiler
def create_mosaic_json(urls):
    files = [
        dict(
            path=l,
        )
        for l in urls
    ]

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        features = [r for r in executor.map(worker, files) if r]

    if features == []:
        print("features is empty, assigning it")
        features = [{'geometry': {'type': 'Polygon',
            'coordinates': [[[-101.00013888888888, 46.00013888888889],
                [-101.00013888888888, 44.999861111111116],
                [-99.9998611111111, 44.999861111111116],
                [-99.9998611111111, 46.00013888888889],
                [-101.00013888888888, 46.00013888888889]]]},
            'properties': {'path': 's3://nasa-maap-data-store/file-staging/nasa-map/SRTMGL1_COD___001/N45W101.SRTMGL1.tif'},
            'type': 'Feature'},
            {'geometry': {'type': 'Polygon',
            'coordinates': [[[-102.00013888888888, 46.00013888888889],
                [-102.00013888888888, 44.999861111111116],
                [-100.9998611111111, 44.999861111111116],
                [-100.9998611111111, 46.00013888888889],
                [-102.00013888888888, 46.00013888888889]]]},
            'properties': {'path': 's3://nasa-maap-data-store/file-staging/nasa-map/SRTMGL1_COD___001/N45W102.SRTMGL1.tif'},
            'type': 'Feature'}]
    else:
        print("features is not empty and is: ")
        print(features)
    
    mosaic_data = MosaicJSON.from_features(features, minzoom=10, maxzoom=18).json()
    mosaic_data_json = json.loads(mosaic_data)
    return mosaic_data_json
    
def create_mosaic_json_from_urls(urls):
    os.environ['CURL_CA_BUNDLE']='/etc/ssl/certs/ca-certificates.crt'
    return MosaicJSON.from_urls(urls)

# Fuction provided by Development Seed. Creates the features for each geoTIFF in the mosaic JSON
def worker(meta):
    try:
        with COGReader(meta["path"]) as cog:
            wgs_bounds = cog.bounds
    except:
        return {}
    return {
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [wgs_bounds[0], wgs_bounds[3]],
                    [wgs_bounds[0], wgs_bounds[1]],
                    [wgs_bounds[2], wgs_bounds[1]],
                    [wgs_bounds[2], wgs_bounds[3]],
                    [wgs_bounds[0], wgs_bounds[3]]
                ]
            ]
        },
        "properties": meta,
        "type": "Feature"
    }

# Adds the specified defaults onto the url taking user input into account. Returns None if errors in the user-given default arguments
def add_defaults_url(url, default_ops, debug_mode):
    if debug_mode and (not errorChecking.check_valid_default_arguments(default_ops)):
        return None

    defaultValues = ""
    temp_defaults_tiler = copy.copy(required_info.defaults_tiler)
    # If given no default_ops, this for loop will not run and all the rest of the default values will just be added
    for key in default_ops:
        defaultValues = defaultValues + "&" + key + "=" + default_ops[key]
        if key in temp_defaults_tiler:
            temp_defaults_tiler.pop(key, None)
            
    # When finished with user's arguments, add the rest of the default values
    for key in temp_defaults_tiler:
        defaultValues = defaultValues + "&" + key + "=" + str(required_info.defaults_tiler[key])
                    
    url = url + defaultValues
    return url