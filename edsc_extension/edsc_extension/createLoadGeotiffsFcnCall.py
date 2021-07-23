"""
This function create the load_geotiffs call after the user presses the button to visualize in CMC after selecting an EarthData search.
This function filters out all invalid urls and only shows the load_geotiffs call with valid urls. This function also adds all defaults 
onto the function call so that the users can edit that data as they please before making the function call to load_geotiffs.
This function also creates info messages for the user to alert them about why certain links were excluded from the function call 
(because of ending and starting file type or data is esa data and will have permission issues). If no valid urls or another error
in this function, function call returns is a comment explaining the error

Written by: Grace Llewellyn, grace.a.llewellyn@jpl.nasa.gov
"""

from . import requiredInfoClass
import sys

global required_info


def create_function_call(urls, maap_var_name):
    """
    Checks if the user given arguments are valid. For the urls, checks that the variable is not empty, all the environments are the same,
    and the file ending is valid. Checks that the class types of the other arguments provided by the user are the correct class type
    Filters out all urls that do not have the correct ending type, starting type, or contain orange-business (all read from variables.json)

    Parameters
    ----------
    urls : list
        The locations of the files in s3 to read from EarthData search. 
    maap_var_name : str
        Default arguments to pass to the Tiler when making the wmts tiles. May be empty (passed by user)
    
    Returns
    -------
    str
        Function call for the user to run or None in case of error
    str
        Info messages to show to the user about what urls were filtered out
    """
    try:
        global required_info
        required_info = requiredInfoClass.RequiredInfoClass(True)
        if not required_info.setup_successful:
            return "# Error evaluating variables.json"
        newUrls, info_message = filter_out_invalid_urls(urls)

        valid, function_call = add_urls((maap_var_name + ".load_geotiffs(urls="), newUrls)
        if not valid:
            return function_call, info_message[1:-1]
        # Add the defaults to the function call
        function_call = function_call + ", default_tiler_ops="+ str(required_info.defaults_tiler) + ", handle_as=\""
        function_call = function_call+required_info.default_handle_as+"\", default_ops_load_layer="+str(required_info.default_ops_load_layer_config)
        function_call = function_call+", debug_mode="+str(required_info.default_debug_mode)+", time_analysis="+str(required_info.default_time_analysis)
        return function_call + ")", info_message[1:-1]
    except:
        return ("# Error creating function call\nError message: " + str(sys.exc_info())), None

def filter_out_invalid_urls(urls):
    """
    Filters out all urls that do not have the correct ending type, starting type, or contain orange-business (all read from variables.json in case they change)

    Parameters
    ----------
    urls : list
        The locations of the files in s3 to read from EarthData search. 
    
    Returns
    -------
    str
        New list of urls with invalid urls filtered out. Can be empty
    str
        Info messages to show to the user about what urls were filtered out. | is used to separate the different info messages
    """
    if isinstance(urls, str):
        urls = list(urls)
    newUrls = []
    info_message = ""
    for url in urls:
        url, new_info_message = determine_single_url_valid(url)
        if url != None:
            newUrls.append(url)
        else:
            info_message = info_message + "|" + new_info_message
    return newUrls, info_message

def determine_single_url_valid(url):
    """
    Determines if the given url is valid by checking its beginning and ending types, and also checking that the data is not esa data because
    permission errors with ESA data in NASA maap. Note that only one error message will be shown to the user for a url that is filtered out.

    Parameters
    ----------
    urls : str
        Single data link to check if valid
    
    Returns
    -------
    str
        The same url given if url is valid for load_geotiffs. If not, None is returned
    str
        Info messages to show to the user about what urls were filtered out
    """
    invalid_end, error_message_end = check_invalid_ending(url)
    if invalid_end:
        return None, error_message_end
    invalid_start, error_message_start = check_invalid_start(url) 
    if invalid_start:
        return None, error_message_start
    invalid_esa_data, error_message_esa_data = check_esa_data(url)
    if invalid_esa_data:
        return None, error_message_esa_data
    return url, None

def check_invalid_ending(url):
    """
    Determines if the given url is valid by checking its ending type and making sure that it's in required_inf.required_ends

    Parameters
    ----------
    urls : str
        Single data link to check if valid ending
    
    Returns
    -------
    bool
        True if the url has an invalid ending and False if not
    str
        Info message for the user about the ending being invalid. None if no info message required because data valid
    """
    for valid_ending in required_info.required_ends:
        if url[len(valid_ending)*-1:] == valid_ending:
            return False, None
    return True, (url + " excluded because doesn't end with one of " + (', '.join([str(elem) for elem in required_info.required_ends])) + ".")

def check_invalid_start(url):
    """
    Determines if the given url is valid by checking its start type and making sure that it's in required_inf.required_start

    Parameters
    ----------
    urls : str
        Single data link to check if valid start
    
    Returns
    -------
    bool
        True if the url has an invalid start and False if not
    str
        Info message for the user about the start being invalid. None if no info message required because data valid
    """
    for valid_start in required_info.required_starts:
        if url[:len(valid_start)] == valid_start:
            return False, None
    return True, (url + " excluded because doesn't end with one of " + (', '.join([str(elem) for elem in required_info.required_starts])) + ".")

def check_esa_data(url):
    """
    Determines if the given url is valid by checking if it contains required_info.esa_data_location which is likely orange-business and means
    that nasa maap will have trouble accessing this data. 

    Parameters
    ----------
    urls : str
        Single data link to check if is esa data
    
    Returns
    -------
    bool
        True if the url is esa data and False if not
    str
        Info message for the user about the url containing esa data. None if no info message required because data valid
    """
    if required_info.esa_data_location in url:
        return False, ("Access not permitted to " + url + " because it is data from ESA.")
    return True, None

def add_urls(function_call, newUrls):
    """
    Adds the urls onto the function call. If there are no urls, makes the functino call a comment telling the user why no urls were able to be found.


    Parameters
    ----------
    function_call : str
        Beginning of function call with varName.load_geotiffs(
    newUrls : list
        List of valid urls to add onto the function call
    
    Returns
    -------
    bool
        True if the url is esa data and False if not
    str
        Info message for the user about the url containing esa data. None if no info message required because data valid
    """
    if len(newUrls) == 0:
        function_call = "# No urls were found that had valid ending types (i.e. one of " + (', '.join([str(elem) for elem in required_info.required_ends]))
        function_call = function_call +") and valid starting types (i.e. one of " + (', '.join([str(elem) for elem in required_info.required_starts]))
        function_call = function_call + ") and didnt' contain " + required_info.esa_data_location + " (ESA data)."
        return False, function_call
    else:
        return True, (function_call + str(newUrls))