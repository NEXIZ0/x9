import subprocess, sys, os
from urllib.parse import urlparse, parse_qs, urlunparse

def run_command_in_zsh(command):
    try:
        result = subprocess.run(["zsh", "-c", command], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Command failed: {result.stderr}")
            return None
        
        return result.stdout.splitlines()
    except Exception as exc:
        print(f"Error: {exc}")
        return None

def remove_duplicate_urls(urls):
    seen = set()
    unique_urls = []

    for url in urls:
        parsed_url = urlparse(url)
        scheme = parsed_url.scheme
        domain = parsed_url.netloc
        path = parsed_url.path
        query = parsed_url.query

        url_identifier = (scheme, domain, path, query)

        if url_identifier not in seen:
            seen.add(url_identifier)
            unique_urls.append(url)
    
    unique_urls.sort(key=lambda u: (urlparse(u).scheme, urlparse(u).netloc, urlparse(u).path, len(urlparse(u).query) > 0))
    
    return unique_urls

def remove_duplicate_scheme(urls):
    seen_urls = {}
    unique_urls = []

    for url in urls:
        original_url = url
        parsed_url = urlparse(url.rstrip('/'))

        scheme = parsed_url.scheme
        domain = parsed_url.netloc
        path = parsed_url.path.rstrip('/')

        query_params = sorted(parse_qs(parsed_url.query).keys())
        query_string = "&".join(query_params)

        url_key = (domain, path, query_string)

        if scheme == 'http' and ('https', *url_key) in seen_urls:
            continue

        if scheme == 'https' and ('http', *url_key) in seen_urls:
            unique_urls.remove(seen_urls[('http', *url_key)])
            del seen_urls[('http', *url_key)]

        seen_urls[(scheme, *url_key)] = original_url
        unique_urls.append(original_url)

    return unique_urls

def remove_slash(urls):
    unique_urls = {}
    
    for url in urls:
        normalized_url = url.rstrip('/')
        has_trailing_slash = url.endswith('/')
        
        if normalized_url in unique_urls:
            if not unique_urls[normalized_url].endswith('/') and has_trailing_slash:
                unique_urls[normalized_url] = url
        else:
            unique_urls[normalized_url] = url
    
    return list(unique_urls.values())

def extract_domains(urls):
    domains = set()
    for url in urls:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if domain:
            domains.add(domain.lower())
    return domains

def nice_katana(urls):
    all_lines = []
    domains = extract_domains(urls)
    for domain in domains:
        command = f"source ~/.zshrc && echo \"{domain}\" | nice_katana | sort -u"
        res = run_command_in_zsh(command)
        if res:
            all_lines.extend(res)

    a = remove_duplicate_urls(all_lines)
    b = remove_duplicate_scheme(a)
    return b

def run_nice_passive(domain, run_katana=False):
    nice_passive_path = "/nexiz/Tools/nice_passive/nice_passive.py"

    result = subprocess.run(['python3', nice_passive_path, domain])
    
    if result.returncode != 0:
        print("Error: nice_passive.py script failed.")
        return

    result_file = f"{domain}.passive"

    if os.path.exists(result_file):
        with open(result_file, 'r') as file:
            urls = file.read().splitlines()

        resultt = remove_duplicate_urls(urls)
        result = remove_duplicate_scheme(resultt)
        last1 = remove_slash(result)
    
        with open(result_file, "w") as file:
            for res in last1:
                file.write(res + '\n')
        
        if run_katana:
            katana = nice_katana(result)

            with open(result_file, "a") as file:
                for rez in katana:
                    file.write(rez + '\n')

            with open(result_file, 'r') as file:
                final = file.read().splitlines()
            
            result1 = remove_duplicate_urls(final)
            result2 = remove_duplicate_scheme(result1)
            last2 = remove_slash(result2)

            with open(result_file, "w") as file:
                for res in last2:
                    file.write(res + '\n')

        # with open(result_file, 'r') as file:
        #     content = file.read()
        #     print(content)
    else:
        print(f"Error: {result_file} not found.")

def print_help():
    help_text = """
Usage: python3 script.py <domain> [-katana] [-h]

Options:
  -katana  Run the script with additional katana processing.
  -h       Display this help message and exit.

Example:
  python3 script.py icollab.info -katana
    """
    print(help_text)

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print_help()
    elif '-h' in sys.argv:
        print_help()
    else:
        domain = sys.argv[1]
        run_katana = '-katana' in sys.argv
        run_nice_passive(domain, run_katana)
