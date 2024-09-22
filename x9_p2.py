import argparse , subprocess
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

def read_file(filepath):
    with open(filepath, 'r') as file:
        return [line.strip() for line in file]
    
def extract_base_urls(urls):
    # Ensure the input is a list
    if isinstance(urls, str):
        urls = [urls]
    
    base_urls = []
    for url in urls:
        parsed_url = urlparse(url)
        # Rebuild the URL without the query and fragment parts
        base_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
        base_urls.append(base_url)
    return base_urls[0] if len(base_urls) == 1 else base_urls


def create_urls_with_parameters(url, parameters):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query, keep_blank_values=True)

    new_urls = []

    for param in parameters:
        for key, values in query_params.items():
            for value in values:
                modified_params = {k: (f"{v[0]}{param}" if k == key else v[0]) for k, v in query_params.items()}
                new_query = "&".join([f"{k}={v}" for k, v in modified_params.items()])
                new_url = urlunparse(parsed_url._replace(query=new_query))
                new_urls.append(new_url)

    return new_urls

def run_command_in_zsh(command):
    try:
        result = subprocess.run(["zsh", "-c", command], capture_output=True, text=True, errors='ignore')
        
        if result.returncode != 0:
            return False

        return result.stdout.splitlines()
    except subprocess.CalledProcessError as exc:
        print("Status : FAIL", exc.returncode, exc.output)

class colors:
    GRAY = "\033[90m"
    RESET = "\033[0m"

def scan_parameters(url):
    command = f"fallparams -u \"{url}\" && cat parameters.txt && rm parameters.txt"
    res = run_command_in_zsh(command)

    res_num = len(res) if res else 0

    return res

def create_urls_with_parameters_fallparams(url, params_from_scan, parameters, chunk_size):
    new_urls = []
    
    parsed_url = urlparse(url)
    base_query_params = parse_qs(parsed_url.query, keep_blank_values=True)

    # Manually add the words to params_from_scan (should be a list)
    additional_params = [
        "begindate" ,"categoryid" ,"checkout_url" ,"continue" ,"currentURL",
        "d" ,"dest" ,"destination" ,"email" ,"enddate" ,"go" ,"id" ,"image",
        "image_rl" ,"key" ,"keyword" ,"keywords" ,"lang" ,"list_type",
        "login" ,"month" ,"name" ,"next" ,"p" ,"page" ,"q" ,"query","redir",
        "redirect" ,"redirect_uri" ,"redirect_url" ,"return" ,"returnTo",
        "return_path" ,"return_to" ,"rurl" ,"s" ,"search" ,"target" ,"terms"
        ,"type" ,"url" ,"view" ,"year" ,"search_box"
    ]

    # Add the additional parameters if they don't already exist in params_from_scan
    for param in additional_params:
        if param not in params_from_scan:
            params_from_scan.append(param)

    # Remove scanned parameters if they exist in the base URL parameters
    filtered_params = [param for param in params_from_scan if param not in base_query_params]
    
    # Update the number of filtered results
    filtered_res_num = len(filtered_params)
    # print(f"Scan Parameter done for \"{url}\", results: {filtered_res_num}")

    for param_value in parameters:
        for i in range(0, len(filtered_params), chunk_size):
            chunk_params = filtered_params[i:i+chunk_size]
            
            query_params = base_query_params.copy()
            
            for param in chunk_params:
                query_params[param] = [param_value]

            new_query = urlencode(query_params, doseq=True)
            new_url = urlunparse(parsed_url._replace(query=new_query))
            new_urls.append(new_url)

    return new_urls

def main():
    parser = argparse.ArgumentParser(description="Process URL and parameters with chunking.")
    
    parser.add_argument('-u', '--url', help='Single URL')
    parser.add_argument('-L', '--list_url', help='File containing list of URLs')
    parser.add_argument('-p', '--parameter', help='Comma-separated list of parameters')
    parser.add_argument('-r', '--list_param', help='File containing list of parameters')
    parser.add_argument('-c', '--chunk', type=int, required=True, help='Chunk number')

    args = parser.parse_args()

    urls = []
    if args.url:
        urls.append(args.url)
    elif args.list_url:
        urls.extend(read_file(args.list_url))
    else:
        print("No URL or URL list provided.")
        return

    parameters = []
    if args.parameter:
        parameters.extend(args.parameter.split(','))
    elif args.list_param:
        parameters.extend(read_file(args.list_param))
    else:
        print("No parameter or parameter list provided.")
        return

    url_bulk = []
    for url in urls:
        #print(f"{colors.GRAY}Simple Permutation for: \"{url}\"{colors.RESET}")
        #print(f"{colors.GRAY}Jaigasht{colors.RESET}")
        generated_urls = create_urls_with_parameters(url, parameters)
        for generated_url in generated_urls:
            url_bulk.append(generated_url)

        max =extract_base_urls(url)

        scanned_params = scan_parameters(max)
        if not scanned_params:
            continue
        #print(f"{colors.GRAY}single{colors.RESET}")
        # Generate URLs with parameters using chunks
        mad_max = create_urls_with_parameters_fallparams(max, scanned_params, parameters, args.chunk)
        for generated_url in mad_max:
            url_bulk.append(generated_url)

        scanned_params = scan_parameters(url)
        if not scanned_params:
            continue
        #print(f"{colors.GRAY}multy{colors.RESET}")
        generated_urls = create_urls_with_parameters_fallparams(url, scanned_params, parameters, args.chunk)
        for generated_url in generated_urls:
            url_bulk.append(generated_url)
        #print("")    
    result_file = f"run.x9"
    with open(result_file, "w") as file:
        for res in url_bulk:
            file.write(res + '\n')

if __name__ == "__main__":
    main()
