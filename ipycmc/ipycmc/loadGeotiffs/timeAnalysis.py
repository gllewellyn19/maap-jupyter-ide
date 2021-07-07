import time 

from . import loadGeotiffs

def conduct_time_analysis(urls, default_ops, debug_mode):
    start = time.perf_counter()
    return_url,handle_as_varjson,default_ops_load_layer_varjson = load_geotiffs_base(urls, default_ops, debug_mode)
    end = time.perf_counter()
    time_debug = end - start

    start = time.perf_counter()
    load_geotiffs_base(urls, default_ops, not debug_mode)
    end = time.perf_counter()
    time_not_debug = end - start

    if debug_mode:
        timing_print_statement(time_debug, time_not_debug)
    else:
        timing_print_statement(time_not_debug, time_debug)
    return return_url,handle_as_varjson,default_ops_load_layer_varjson

def timing_print_statement(time_debug, time_not_debug):
    output = f"The time for debug mode was {time_debug:0.5f} and the time for non debug mode was {time_not_debug:0.5f}. "
    if time_debug > time_not_debug:
        output = output + f" Not debugging was {time_debug-time_not_debug:0.5f} faster than debugging."
    else:
        output = output + f" Debugging was {time_not_debug-time_debug:0.5f} faster than not debugging."
    print(output)