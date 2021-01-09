import requests
import re
import json
import optparse
import sys
import validators
import tldextract

BLUE='\033[94m'
GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
CLEAR='\x1b[0m'

print(BLUE + "dmass[1.2] by ARPSyndicate" + CLEAR)
print(GREEN + "scrapes domains from VDP/BBP scopes" + CLEAR)

parser = optparse.OptionParser()
parser.add_option('-s', '--sources', action="store", dest="sources", help="sources to scrape [disclose,arkadiyt,chaos,crawlerninja,kaas]", default="disclose,arkadiyt,chaos,crawlerninja,kaas")
parser.add_option('-v', '--verbose', action="store_true", dest="verbose", help="enable logging", default=False)
parser.add_option('-r', '--root-domains-only', action="store_true", dest="root", help="scrape root domains only", default=False)
parser.add_option('-o', '--output', action="store", dest="output", help="file for storing the output", default=False)

inputs, args = parser.parse_args()
sources = str(inputs.sources).split(",")
verbose = inputs.verbose
output = str(inputs.output)


domains =[]

def disclose():
    print(YELLOW+"[*] scraping from disclose"+CLEAR)
    global domains
    src = "https://data.disclose.io/diosts/10M/"
    response = requests.get(src)
    match = re.findall('(?<=\>)diosts.*\.json', response.text, re.IGNORECASE)
    data = requests.get(src+match[-1]).text
    if(data[-2] != "]"):
        data+="]"
    data = json.loads(data)

    for meta in data:
        if verbose:
            print(BLUE + "[+] [disclose] " + meta['security_txt_domain'] + CLEAR)
        domains.append(meta['security_txt_domain'])

def arkadiyt():
    print(YELLOW+"[*] scraping from arkadiyt"+CLEAR)
    global domains
    src = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/domains.txt"
    response = requests.get(src).text
    data = response.splitlines()
    if verbose:
        for domain in data:
            print(BLUE + "[+] [arkadiyt] " + domain + CLEAR)
    domains.extend(data)
    
def chaos():
    print(YELLOW+"[*] scraping from chaos"+CLEAR)
    global domains
    src = "https://raw.githubusercontent.com/projectdiscovery/public-bugbounty-programs/master/chaos-bugbounty-list.json"
    data = requests.get(src).json()
    for meta in data["programs"]:
        if verbose:
            for domain in meta['domains']:
                print(BLUE + "[+] [chaos] " + domain + CLEAR)
        domains.extend(meta['domains'])

def crawlerninja():
    print(YELLOW+"[*] scraping from crawlerninja"+CLEAR)
    global domains
    src = "https://crawler.ninja/files/security-txt-sites.txt"
    data = requests.get(src).text
    data = data.splitlines()
    for meta in data[1:]:
        domain = meta.split(" ")[1]
        if verbose:
            print(BLUE + "[+] [crawlerninja] " + domain + CLEAR)
        domains.append(domain)

def kaas():
    print(YELLOW+"[*] scraping from kaas"+CLEAR)
    global domains
    src = "https://raw.githubusercontent.com/ARPSyndicate/KaaS/master/huntdb_domains.txt"
    response = requests.get(src).text
    data = response.splitlines()
    if verbose:
        for domain in data:
            print(BLUE + "[+] [kaas] " + domain + CLEAR)
    domains.extend(data)


def dump():
    print(YELLOW+"[*] dumping output"+CLEAR)
    global domains
    if inputs.root:
        nce = tldextract.TLDExtract(cache_dir=False)
        domains = ["{}.{}".format(nce(domain).domain, nce(domain).suffix) for domain in domains if validators.domain(domain)== True]
    domains=list(set(domains))
    domains.sort()
    with open(output, 'w') as f:
        f.writelines("%s\n" % domain for domain in domains if validators.domain(domain)== True)

if "disclose" in sources:
    disclose()
if "arkadiyt" in sources:
    arkadiyt()
if "chaos" in sources:
    chaos()
if "crawlerninja" in sources:
    crawlerninja()
if "kaas" in sources:
    kaas()
if inputs.output:
    dump()
else:
    print(RED+"[!] no output file was provided"+CLEAR)

print(YELLOW+"[*] done"+CLEAR)