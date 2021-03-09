apikey='GOJKUKZEAK5QIOUW'
def readdata():
    from alpha_vantage.timeseries import TimeSeries
    ts = TimeSeries(key=apikey,output_format='pandas')
    
