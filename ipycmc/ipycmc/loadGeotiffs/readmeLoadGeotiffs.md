# README for load\_geotiff function
## Arguments
MapCMC.load\_geotiffs(urls, default\_ops (Optional), handle\_as (Optional), default\_ops\_load\_layer (Optional)).
Function call must be on a MapCMC object.
* Urls, where urls must be:
	*  a string consisting of a single link to a geotiff in an s3 bucket in the MAAP ade (private or bucket bucket will suffice). Currently, this string must start with "s3://" and end with ".tif" or ".tiff". However, this can be changed by modifying the `required_start` and `required_end` lists in variables.json. Even if these arguments are changed, if the beginning and ending types of the links do not comply with the TiTiler requirements, an error message will be returned.
    * a list consisting of links to geotiffs where each link follows all the guidlines listed above 
    * a string pointing to a folder in an s3 bucket. All files in this folder will be added to a list as long as they end in one of `required_end`
* default\_ops
	* tile\_format
   * tile\_scale
   * pixel\_selection 
   * TileMatrixSetId
   * resampling\_method 
   * return\_mask
   * rescale
   
    __Additional arguments you can add that are not typically added as defaults (Note: you can change the defaults by modifying `defaults_tiler` in variables.json:)__
   * minzoom 
   * maxzoom 
   * bidx 
   * expression 
   * nodata 
   * unscale 
   * color\_formula
   * colormap\_name 
   * colormap
   
   __For more documentation about these arguments, please visit:__
   
 * handle\_as
    * Default is "wmts/xml", but this can be changed by modifying `default_handle_as` in variables.json 
  * default\_ops\_load\_layer
  	* Default is `{"handleAs": "wmts_raster"}`, but this can be changed by modifying `default_ops_load_layer` in variables.json
    
## Objective of this function
The goal of load\_geotiffs is to take in the location of a geotiff in a MAAP ade s3 bucket and create a request url to a TiTiler endpoint (depending on MAAP environment). This request url points to an XML file that represents a WMTS capabilities file for the geotiff. This is passed to load\_layer\_config. A layer is loaded into CMC in a single seamless function call that can handle multiple geotiffs. In order for CMC to correctly display the tile request, certain default arguments need to be added onto this request url. In the case of a single geotiff, this is simple as the s3 link is added to the request url as a argument along with the default arguments. However, in the case of multiple geotiffs, a mosaic JSON must be created. The mosaic JSON is created through the from\_urls or from\_features methods in the cogeo\_mosaic library created by Development seed. The mosaic JSON is then posted to a TiTiler endpoint where a WMTS capabilities link is returned. The default arguments are added to this WMTS capabilities link and then passed to load\_layer\_config as the request url. A user can always change the default arguments as described above. 

## Error checking performed by load\_geotiffs
##### Variables.json
* All required keys are present in variables.json. Required keys can be found in the file `loadGeotiffs/requiredInfoClass.py`.
* All of the required keys are non-empty.
* All TiTiler endpoints (`posting_tiler_endpoint`, `endpoint_published_data`, `endpoints_tiler.values()`) begin with one of `web_starts` (i.e. https:// or http://)
##### General argument checking
* Urls is either string or list
* Urls is non-empty
* Urls (and every element if list) begins with one of `required_starts`
* If list of urls, each element has the same s3 bucket name
* One of the keys passed for `default_ops` is not found as a valid key in `defaults_tiler` or `accepted_arguments_tiler`
* One of the parameters passed for `default_ops` is not the correct class type 
* One of the parameters passed for `default_ops` is not one of the values accepted for the finite list of accepted arguments (i.e. for the parameters `TileMatrixSetId`, `resampling_method`, `colormap_name`, `tile_format`, and `pixel_selection`)

##### More advanced argument error checking
* s3 bucket name of s3 link is not one of `endpoints_tiler.keys()`
* The bucket name cannot be found in the s3 link because of incorrect amount of "/"s

##### Errors with request url
* If the information at request url does not begin with an xml beginning then the json formatted error message for the TiTiler is printed. This json formatted error message might be one of the known TiTiler errors and have a translated response with explaination, or it may just be the exact TiTiler error. 

##### Errors with s3 bucket folder as urls
* Access denied when trying to read through buckets of given s3 bucket environment
* No geotiffs in given folder (i.e. no files have any of `required_ends`)

##### Errors with multiple s3 links
* Any one of the individual s3 links cannot be correctly completed in a single geotiff tiler request (this is likely an access denied error, but the exact tiler error message will be printed)

## Documentation for variables.json
* `required_starts`: How the urls must begin in order for function to complete successfully
* `required_ends`: Hows the urls must end in order for function to complete successfully. Note that in the case of a folder for urls, the folder should not end in one of `required_ends`, but the contents of the folder should end in one of `required_ends`
 * `defaults_tiler`: The default values to pass in the request url to the tiler represented as a dictionary where the key is the name of a variable that the tiler accepts and the value is the value of that variable. Note that these values can be provided by the user. If these values are not provided by the user, they will be passed into the request url as is from this variable. This is because the tiles may not display without these defaults, especially the `rescale` option.
 * `endpoints_tiler`: Dictionary where the key representing the workspace bucket name of MAAP ade environments supported by this function and the values represent the tiler endpoint that these environments are compatible with. Note that currently only gcc ops and Pilot ops are supposed by this function (maap-ops-workspace found at [https://ade.ops.maap-project.org/](https://ade.ops.maap-project.org/) and maap-ops-dataset found at [https://ade.maap-project.org/](https://ade.maap-project.org/))
 * `tiler_extensions`: Since a user can either pass a singel geotiff or multiple geotiffs, this variable indicates the extension to the request url to the TiTiler for either a single geotiff or multiple geotiffs. These representing supported extensions to TiTiler endpoints.
 * `endpoint_published_data`: This represents the TiTiler endpoint to used for published data. Unlike `endpoints_tiler` published data doesn't need to use a certain TiTiler endpoint. By default it uses the Tiler ops endpoint, but that can be changed at any time by modifying this variable.
 * `posting_tiler_endpoint`: This represents the TiTiler endpoint that has the capability of posting a mosaicjson and receiving the link later
 * "https://h9su0upami.execute-api.us-east-1.amazonaws.com",
    "errors_tiler": {"not recognized as a supported file format.":"You have entered an invalid file path that does not exist or the TiTiler does not have access to.", "Access Denied":"The Tiler does not have access to the file path that you have provided, please give a maap s3 bucket or published data."},
    "accepted_arguments_tiler":["minzoom", "maxzoom", "bidx", "expression", "nodata", "unscale", "color_formula", "colormap_name", "colormap"],
    "mosaicjson_file_name":"mosaicjson.json",
    "xml_beginning":"<",
    "general_error_warning_tiler":"There was an error reading your link and Tiler gave the following error message: ",
    "required_class_types_args_tiler":{"tile_scale":"int", "minzoom":"int", "maxzoom":"int", "bidx":"str", "expression":"str", "unscale":"bool", "rescale":"str", "color_formula":"str", "return_mask":"bool", "colormap":"str", "tile_format":"str", "TileMatrixSetId":"str", "resampling_method":"str", "colormap_name":"str", "pixel_selection":"str"},
    "tile_format":["png", "jpg", "jpeg", "tif", "jp2", "npy", "webp", "pngraw"],
    "pixel_selection":["first", "highest", "lowest", "mean", "median", "stdev"],
    "getting_xml_endpoint":"list(filter(lambda x: x.get('rel') == 'wmts', dict(r)['links']))[0].get('href')",
    "web_starts":["https://", "http://"],
    "default_handle_as": "wmts/xml",
    "default_ops_load_layer_config": {"handleAs": "wmts_raster"}
   }
   
### Debug mode
Running not in debug mode is a risk if you do not understand how the function works since there is minimal error checking and you are not provided with detailed responses. If you receive an error message you do not understand, run the problem in debug mode. Debug mode is enabled by default.

### Time analysis
The only difference setting this parameter to True is that the function call is done twice (once with debug mode and once without) and the results are printed. The request url generated for the given parameters including the given `debug_mode` are sent to  load\_layer\_config as the function normally does. This function takes longer to run and the only purpose of it is to show the effects of `debug_mode` so that users can decide if they would like to run in that mode. Note that `time_analysis` is False by default. 

### Troubleshooting
Rerun the loadGeotiff function if the map layer does not show up the first time.

### To do
* Find best way to show function parameters and mark as optional at the top
* Maybe use from urls or from features depending on the file size
* Find documentation about handle as and default ops for load layer config
* Change tiler to TiTiler

* What happens if I pass https:// to Tiler?
* Add default handle\_as and default ops for load layer
* Try Except in error reading from bucket
* Make required\_ends and starts

### Questions
How much should I describe the default ops
