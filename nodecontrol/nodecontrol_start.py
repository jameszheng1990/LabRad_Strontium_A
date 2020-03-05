import labrad 
import numpy as np
import time
from nodecontrol_config import node_dict
import os

cxn = labrad.connect(host=os.getenv('LABRADHOST'), password='')
for node in node_dict.keys():
    if node in cxn.servers: 
        print('{}:'.format(node))
        cxn.servers[node].refresh_servers()
        running_servers = np.array(cxn.servers[node].running_servers())
        for server in node_dict[node]:
            if server in running_servers: 
                print('{} is running'.format(server))
            else:
                print('starting ' + server)
                try:
                    cxn.servers[node].start(server)
                except Exception as e:
                    print('error with ' + server)
                    print(e)
    else:
        print('{} is not running'.format(node))

print('done!')
