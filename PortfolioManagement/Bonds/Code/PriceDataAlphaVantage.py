from alpha_vantage.timeseries import TimeSeries

key = 'OVMZPRA3SKDOPBHU'

ts = TimeSeries(key)

print(ts.get_quote_endpoint("NN6EUR"))

