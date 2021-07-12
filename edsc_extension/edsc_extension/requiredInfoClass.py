"""
This class holds all the parameters that are necessary to operate the load_geotiffs function

Written by Grace Llewellyn
"""
import json
import requests
from rasterio.enums import Resampling
from rio_tiler.colormap import cmap
import os
import sys

path_variablesjson = "ipycmc/ipycmc/loadGeotiffs/variables.json"

class RequiredInfoClass:
    def __init__(self, debug_mode):
        try:
            print(os.path.abspath(__file__).replace("edsc_extension/edsc_extension/"+os.path.basename(__file__), path_variablesjson))
            f = open(os.path.abspath(__file__).replace("edsc_extension/edsc_extension/"+os.path.basename(__file__), path_variablesjson), "r")
            dictionary = json.loads(f.read())
        except:
            print("JSON file with variable information could not be found.")
            self.setup_successful = False
            return
        
        try:
            # Initialize all the variables
            self.required_starts = dictionary["required_starts"]
            self.required_ends = dictionary["required_ends"]
            self.defaults_tiler = dictionary["defaults_tiler"]
            self.endpoints_tiler = dictionary["endpoints_tiler"]
            self.tiler_extensions = dictionary["tiler_extensions"]
            self.endpoint_published_data = dictionary["endpoint_published_data"]
            self.posting_tiler_endpoint = dictionary["posting_tiler_endpoint"]
            self.errors_tiler = dictionary["errors_tiler"]
            self.accepted_parameters_tiler = dictionary["accepted_parameters_tiler"]
            self.general_error_warning_tiler = dictionary["general_error_warning_tiler"]
            self.required_class_types_args_tiler = dictionary["required_class_types_args_tiler"]
            self.correct_wmts_beginning = dictionary["correct_wmts_beginning"]
            self.accepted_arguments_default_ops = {"TileMatrixSetId":[(entry["id"]) for entry in requests.get("https://api.cogeo.xyz/tileMatrixSets").json()["tileMatrixSets"]], 
                                 "resampling_method": [(r.name) for r in Resampling], 
                                 "colormap_name": cmap.list(),
                                 "tile_format_args":dictionary["tile_format_args"],
                                 "pixel_selection_args":dictionary["pixel_selection_args"]}
            self.getting_wmts_endpoint = dictionary["getting_wmts_endpoint"]
            self.web_starts = dictionary["web_starts"]
            self.handle_as = dictionary["default_handle_as"]
            self.default_ops_load_layer_config = dictionary["default_ops_load_layer_config"]

        except:
            print("Essential key missing from JSON file: " + str(sys.exc_info()[1]))
            self.setup_successful = False
            return

        self.setup_successful = True
        if debug_mode:
            self.check_non_empty_all()
            self.other_error_checking([self.posting_tiler_endpoint, self.endpoint_published_data] + list(self.endpoints_tiler.values()))
        
    # Note that not all variables are required to be non empty
    # Print all variables that are empty that need to be filled at once for the user
    def check_non_empty_all(self):
        to_return = True
        variables = vars(self)
        for key in variables:
            if not variables[key]:
                print("Cannot pass an empty value for " + key + " in variables.json file.")
                to_return = False
        return to_return
    
    def other_error_checking(self, links):
        for link in links:
            start_found = False
            for web_start in self.web_starts:
                if link.startswith(web_start):
                    start_found = True
                    break
            if not start_found:
                print(link + " in variables.json must start with one of " + (', '.join([str(web_start) for web_start in self.web_starts])) + " to be considered a link.")
                self.setup_successful = False