import requests
from collections import defaultdict
import json
import pandas as pd


def populate_district_codes():
    state_ids_url = "https://cdn-api.co-vin.in/api/v2/admin/location/states"
    state_ids = json.loads(requests.get(state_ids_url).content)
    district_url = "https://cdn-api.co-vin.in/api/v2/admin/location/districts/{}"
    state_info = defaultdict(dict)
    for state in state_ids['states']:
        state_id = state['state_id'] 
        dis_url = district_url.format(state_id)
        district_info = json.loads(requests.get(dis_url).content)
        state_info[state['state_name']] = district_info['districts']
    fh = open('district_codes.md', 'w+')
    for state in state_info:
        df = pd.DataFrame(state_info[state])
        fh.write(f'#{state}\n\n')
        content = df.to_markdown(mode='a', index=False, tablefmt="grid")
        fh.write(content)
        fh.write("\n\n")
populate_district_codes()
