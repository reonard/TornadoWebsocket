__author__ = 'reonard'

import re

m = re.search(r'(.*)-:-(.*)', 'HB-:-TerminalID')

if m:
    print(m.group(2))