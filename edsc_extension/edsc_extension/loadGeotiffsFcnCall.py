from . import requiredInfoClass

global required_info


def create_function_call(urls):
    # Filter out all urls that do not have the correct ending type
    global required_info
    required_info = import_variablesjson()
    newUrls = filter_out_invalid_urls(urls)

    # Add urls
    function_call, valid = add_urls("w.load_geotiffs(urls=", newUrls)
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
    newUrls = []
    for url in urls:
        for valid_ending in required_info.required_ends:
            if url[len(valid_ending)*-1:] == valid_ending:
                newUrls.append(url)
                break
    print(str(newUrls) + " after error check for ending")
    return newUrls

def add_urls(function_call, newUrls):
    if len(newUrls) == 0:
        function_call = "No urls were found and had valid ending types (i.e. one of " + (', '.join([str(elem) for elem in required_info.required_ends])) + ")."
        return function_call, False
    elif len(newUrls) == 1:
        function_call = function_call + "\"" + newUrls + "\""
    elif len(newUrls) > 1:
        function_call = function_call + str(newUrls)
    return function_call, True