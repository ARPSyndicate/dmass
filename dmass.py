import requests
import re
import json
import optparse
import sys

BLUE='\033[94m'
GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
CLEAR='\x1b[0m'

print(BLUE + "dmass[1.0] by ARPSyndicate" + CLEAR)
print(GREEN + "scrapes domains from VDP/BBP scopes" + CLEAR)

parser = optparse.OptionParser()
parser.add_option('-s', '--sources', action="store", dest="sources", help="sources to scrape [disclose,arkadiyt,chaos]", default="disclose,arkadiyt,chaos")
parser.add_option('-v', '--verbose', action="store_true", dest="verbose", help="enable logging", default=False)
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
            print(BLUE + "[+] [disclose] " + meta['program_name'] + CLEAR)
        domains.append(meta['program_name'])

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

def dump():
    print(YELLOW+"[*] dumping output"+CLEAR)
    global domains
    domains=list(set(domains))
    domains.sort()
    with open(output, 'w') as f:
        f.writelines("%s\n" % domain for domain in domains)

if "disclose" in sources:
    disclose()
if "arkadiyt" in sources:
    arkadiyt()
if "chaos" in sources:
    chaos()
if inputs.output:
    dump()
else:
    print(RED+"[!] no output file was provided"+CLEAR)

print(YELLOW+"[*] done"+CLEAR)