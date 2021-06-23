
import boto3
from . import errorChecking

global required_info

def initialize_required_info(required_info_given):
    global required_info
    required_info = required_info_given

# Extracts the list of geotiff links from the folder path. Returns None if the folder path is not reachable and only returns the names of files that end in
# required_end_s3_link_lowercase or required_end_s3_link_uppercase
def extract_geotiff_links(folder_path):
    bucket_name = errorChecking.determine_valid_bucket(folder_path)
    if bucket_name == None:
        print("The environment of the bucket you passed as a folder is not a valid environment type. The supported environments are: " +  
            (', '.join([str(key) for key in required_info.endpoints_tiler])) + ".")
        return []
    file_path = get_file_path_folder(folder_path)

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    geotiff_links = []
    for obj in bucket.objects.filter(Prefix=file_path):
        if obj.size and file_ending(obj.key): 
            geotiff_links.append(required_info.required_start[0] + bucket_name + "/" + obj.key)

    print("Geotiff links extracted from given folder are "+geotiff_links)
    return geotiff_links

    
# Extracts the bucket name from the s3 link and prints the appropriate error message if the bucket name cannot be found
def extract_bucket_name(s3Link):
    location_start_bucket_name = len(required_info.required_start[0])
    if s3Link[location_start_bucket_name:].find("/") == -1:
        #print("Your s3 link does not contain a / to separate the bucket name from the key name. Please provide a correct s3 link. Example: s3://maap-ops-workspace/graceal/filename.tiff")
        return None
    location_end_bucket_name = s3Link[location_start_bucket_name:].find("/") + len(required_info.required_start[0])
    return s3Link[location_start_bucket_name:location_end_bucket_name]

# Determines the environment of the given link by extracting the bucket name and referring to a constant dictionary for the corresponding Tiler endpoint
# Returns None in the case that the s3 bucket cannot be found. Assumed to be published data in this case. 
# Prints the appropriate error message if the given environment is not provided. For supported environments, see the dictionary constant endpoints_tiler in this file
def determine_environment(s3Link):
    bucket_name = extract_bucket_name(s3Link)
    if bucket_name == None:
        return None
    endpoint_tiler = required_info.endpoints_tiler.get(bucket_name)
    if endpoint_tiler == None:
        #print("Environment not supported by this function. For supported s3 buckets try: "+get_supported_environments() + ". You may also pass published s3 links.")
        return None
    return endpoint_tiler

# Assumes that there is not multiple different s3 buckets in the list of urls because this was already checked for
def determine_environment_list(urls):
    for url in urls:
        # When you find the first occurrence of an S3 bucket, return that url
        if determine_environment(url) != None:
            return determine_environment(url)
    # All links are published if no s3 environments found- this means any endpoint can be returned (Choosing to return ops at the moment)
    return required_info.endpoint_published_data

# Returns False if the ending type of the file is not .tif or any other valid ending type and True if it is
def file_ending(s3Link):
    for valid_ending in required_info.required_end:
        if s3Link[len(valid_ending)*-1:] == valid_ending:
            return True
    return False

# Assumes that the folder exists in a valid bucket and gives the file path without the s3://bucket-name from the url 
def get_file_path_folder(url):
    file_path = url[len(required_info.required_start[0]):]
    ending_bucket_name = file_path.find("/")
    file_path = file_path[ending_bucket_name+1:]
    return file_path