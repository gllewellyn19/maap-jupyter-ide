from . import requiredInfoClass

global required_info


def create_function_call(urls, maap_var_name):
    # Filter out all urls that do not have the correct ending type
    global required_info
    required_info = import_variablesjson()
    if not required_info.setup_successful:
        return "# Error evaluating variables.json"
    newUrls = filter_out_invalid_urls(urls)

    # Add urls
    function_call, valid = add_urls((maap_var_name + ".load_geotiffs(urls="), newUrls)
    if not valid:
        return function_call
    function_call = function_call + ", default_tiler_ops="+ str(required_info.defaults_tiler) + ", handle_as=\""
    function_call = function_call+required_info.default_handle_as+"\", default_ops_load_layer="+str(required_info.default_ops_load_layer_config)
    function_call = function_call+", debug_mode="+str(required_info.default_debug_mode)+", time_analysis="+str(required_info.default_time_analysis)

    return function_call + ")"

def import_variablesjson():
    # TODO fix this to call the right required info
    required_info = requiredInfoClass.RequiredInfoClass(True)
    return required_info

def filter_out_invalid_urls(urls):
    if isinstance(urls, str):
        if check_valid_ending(urls) and check_valid_start(urls) and check_not_esa_data(urls):
            return urls
        else:
            return []
    newUrls = []
    for url in urls:
        if check_valid_ending(url) and check_valid_start(url) and check_not_esa_data(url):
            newUrls.append(url)

    print(str(newUrls) + " after error check for ending")
    return newUrls

def check_valid_ending(url):
    for valid_ending in required_info.required_ends:
        if url[len(valid_ending)*-1:] == valid_ending:
            return True
    print(url + " excluded because doesn't end with one of " + (', '.join([str(elem) for elem in required_info.required_ends])) + ".")
    return False

def check_valid_start(url):
    for valid_start in required_info.required_starts:
        if url[:len(valid_start)] == valid_start:
            return True
    print(url + " excluded because doesn't end with one of " + (', '.join([str(elem) for elem in required_info.required_starts])) + ".")
    return False

def check_not_esa_data(url):
    if "orange-business" in url:
        print("Access not permitted to " + url + " because it is data from ESA.")
        return False
    return True

def add_urls(function_call, newUrls):
    if len(newUrls) == 0:
        function_call = "# No urls were found that had valid ending types (i.e. one of " + (', '.join([str(elem) for elem in required_info.required_ends]))
        function_call = function_call +") and valid starting types (i.e. one of " + (', '.join([str(elem) for elem in required_info.required_starts]))
        function_call = function_call + ") and didnt' contain orange-business (ESA data)."
        return function_call, False
    elif isinstance(newUrls, str):
        function_call = function_call + "\"" + newUrls + "\""
    elif len(newUrls) == 1:
        function_call = function_call + "\"" + newUrls[0] + "\""
    elif len(newUrls) > 1:
        function_call = function_call + str(newUrls)
    return function_call, True