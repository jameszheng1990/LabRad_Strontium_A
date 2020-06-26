"""
### BEGIN NODE INFO
[info]
name = plotter
version = 1.0
description = 
instancename = plotter

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

import imp
import json
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import os
from io import StringIO
from time import time

from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory
from labrad.server import setting
from twisted.internet import reactor


from server_tools.threaded_server import ThreadedServer

WEBSOCKET_PORT = 9000
PROJECT_DATA_PATH = os.path.join(os.getenv('LABRADDATA'), 'data')

class MyServerProtocol(WebSocketServerProtocol):
    connections = list()

    def onConnect(self, request):
        self.connections.append(self)
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")
    
    @classmethod
    def send_figure(cls, figure):
        print('num connections', len(cls.connections))
        for c in set(cls.connections):
            reactor.callFromThread(cls.sendMessage, c, figure, False)
    
    @classmethod
    def close_all_connections(cls):
        for c in set(cls.connections):
            reactor.callFromThread(cls.sendClose, c)
    
    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

        # echo back message verbatim
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        self.connections.remove(self)
        print("WebSocket connection closed: {0}".format(reason))

class PlotterServer(ThreadedServer):
    name = 'plotter'
    is_plotting = False
    data= []

    def initServer(self):
        """ socket server """
        # url = u"ws://0.0.0.0:{}".format(WEBSOCKET_PORT)
        # factory = WebSocketServerFactory()
        # factory.protocol = MyServerProtocol
        # reactor.listenTCP(WEBSOCKET_PORT, factory)
    
    def stopServer(self):
        """ socket server """
        # MyServerProtocol.close_all_connections()

    @setting(0)
    def plot(self, c, settings_json='{}'):
        settings = json.loads(settings_json)
        if not self.is_plotting:
            reactor.callInThread(self._plot, settings)
        else:
            print('still making previous plot')

    def _plot(self, settings):
        try:
            self.is_plotting = True
    
            path = settings['plotter_path']
            process_function_name = settings['processer_function']
            plot_function_name = settings['plotter_function']
            module_name = os.path.split(path)[-1].strip('.py')
            
            # print(settings)
            # print(path)
            # print(module_name)
            
            module = imp.load_source(module_name, path)
            process_function = getattr(module, process_function_name)
            plot_function = getattr(module, plot_function_name)
            
            shot = settings['shot']
            to_plot = settings['to_plot']
            
            if shot >= 0:
                print('Processing data...')
                subdata = process_function(settings)
                if shot == 0:
                    self.data = []
                self.data.extend(subdata)
                        
            if to_plot and len(self.data):
                print('Plotting result...')
                plot_function(self.data, settings)
                
            # fig = function(settings)
            # save_dir = os.path.join(PROJECT_DATA_PATH, settings['data_path'], 'plot')
            # if not os.path.isdir(save_dir):
            #     os.makedirs(save_dir)
            # save_path = os.path.join(save_dir, os.path.split(settings['data_path'])[0] + '_' + os.path.split(settings['data_path'])[1])
            # print(save_dir)
            # print(save_path)
            
            # sio = StringIO.StringIO()
            # fig.savefig(sio, format='svg')
            # sio.seek(0)
            # figure_data = sio.read()
            # MyServerProtocol.send_figure(figure_data)
            # plt.close(fig)
            # del fig
            # del sio
            # del figure_data
            self.is_plotting = False
        except Exception as e:
            self.is_plotting = False
            raise e
Server = PlotterServer

if __name__ == "__main__":
    from labrad import util
    util.runServer(Server())
