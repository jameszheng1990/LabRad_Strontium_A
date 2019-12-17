class config(object):
    
    def set_clk(self):
        clk = 100e3     # [Hz]
        return clk
    
    def get_key(self):
        key = 'CLK@Z_CLK00'
        return key
    
    def set_do_rate(self):
        rate = 50e3    # [Hz], should be half of clk
        return rate
    
    def set_ao_rate(self):
        rate = 50e3    # [Hz] Should be half of the Clk
        return rate