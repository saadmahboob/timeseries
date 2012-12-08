from unittest import TestCase
from timeseries import TimeSeries, TimeSeriesGroup
from datetime import datetime

class TestTimeSeries(TestCase):

    def test_frequency(self):
        series = TimeSeries([], frequency=3)
        self.assertEquals(series.frequency, 3)

    def test_tuple_list_init(self):
        series = TimeSeries([ (1, 2), (3, 4), (5, 6) ])
        self.assertListEqual(series.x, [1, 3, 5])
        self.assertListEqual(series.y, [2, 4, 6])
        self.assertEquals(len(series), 3)

    def test_dict_init(self):
        series = TimeSeries({ 1: 2, 3: 4, 5: 6 })
        self.assertListEqual(series.x, [1, 3, 5])
        self.assertListEqual(series.y, [2, 4, 6])
        self.assertEquals(len(series), 3)

    def test_accessors(self):
        points = [ (1234000, 54), (5678000, 100) ]
        series = TimeSeries(points)
        dates = series.dates
        for date in dates:
            self.assertTrue(isinstance(date, datetime))
        self.assertListEqual(series.dates, [datetime.fromtimestamp(1234),
            datetime.fromtimestamp(5678)])
        self.assertListEqual(series.timestamps, [1234000, 5678000])
        self.assertListEqual(series.values, [54, 100])

    def test_interval(self):
        series = TimeSeries([])
        self.assertEquals(series.interval, None)
        series = TimeSeries([ (1, 2) ])
        self.assertEquals(series.interval, None)
        series = TimeSeries([ (1, 2), (3, 4) ])
        self.assertEquals(series.interval, 2)

    def test_iteration(self):
        points = [ (1, 2), (3, 4), (5, 6) ]
        series = TimeSeries(points)
        self.assertListEqual([ s for s in series ], points)

    def test_trend_return_type(self):
        trend = TimeSeries([ (1, 3), (2, 5) ]).trend(order=TimeSeries.LINEAR)
        self.assertTrue(isinstance(trend, TimeSeries))

    def test_invalid_forecast_method(self):
        series = TimeSeries([ (1, 100), (2, 200), (3, 100), (4, 200), (5, 100) ])
        with self.assertRaises(ValueError):
            forecast = series.forecast(7, method='huh')

    def test_forecast_on_empty_series(self):
        with self.assertRaises(ArithmeticError):
            series = TimeSeries([])
            forecast = series.forecast(7)

    def test_arima_forecast_without_frequency(self):
        series = TimeSeries([ (1, 100), (2, 200), (3, 100), (4, 200), (5, 100) ])
        forecast = series.forecast(3, method=TimeSeries.ARIMA)
        self.assertTrue(isinstance(forecast, TimeSeries))
        self.assertListEqual(forecast.timestamps, [6, 7, 8])
        #self.assertListEqual(forecast.values, [])

    def test_arima_forecast_with_frequency(self):
        series = TimeSeries([ (1, 100), (2, 200), (3, 100), (4, 200), (5, 100) ], frequency=4)
        forecast = series.forecast(3, method=TimeSeries.ARIMA)
        self.assertTrue(isinstance(forecast, TimeSeries))
        self.assertListEqual(forecast.timestamps, [6, 7, 8])
        #self.assertListEqual(forecast.values, [])

    def test_ets_forecast_without_frequency(self):
        series = TimeSeries([ (1, 100), (2, 200), (3, 100), (4, 200), (5, 100) ])
        forecast = series.forecast(3, method=TimeSeries.ETS)
        self.assertTrue(isinstance(forecast, TimeSeries))
        self.assertListEqual(forecast.timestamps, [6, 7, 8])
        #self.assertListEqual(forecast.values, [])

    def test_ets_forecast_with_frequency(self):
        series = TimeSeries([ (1, 100), (2, 200), (3, 100), (4, 200), (5, 100) ], frequency=4)
        forecast = series.forecast(3, method=TimeSeries.ETS)
        self.assertTrue(isinstance(forecast, TimeSeries))
        self.assertListEqual(forecast.timestamps, [6, 7, 8])
        #self.assertListEqual(forecast.values, [])

    def test_decomposition_with_no_frequency(self):
        series = TimeSeries([ (1, 2), (3, 4) ])
        with self.assertRaises(ValueError):
            series.decompose()

    def test_decomposition(self):
        series = TimeSeries([ (1, 100), (2, 200), (3, 100), (4, 200), (5, 100) ], frequency=2)
        decomposed = series.decompose()
        self.assertTrue(isinstance(decomposed, TimeSeriesGroup))
        self.assertEquals(len(decomposed), 3)
        for series in decomposed.itervalues():
            self.assertListEqual(series.timestamps, [1, 2, 3, 4, 5])
        self.assertListEqual(decomposed['trend'].values, [150] * 5)
        self.assertListEqual(decomposed['seasonal'].values, [-50, 50, -50, 50, -50])
        self.assertListEqual(decomposed['residual'].values, [0] * 5)

    def test_periodic_decomposition(self):
        series = TimeSeries([ (1, 100), (2, 200), (3, 100), (4, 200), (5, 100) ], frequency=2)
        decomposed = series.decompose(periodic=True)
        self.assertTrue(isinstance(decomposed, TimeSeriesGroup))
        self.assertEquals(len(decomposed), 3)
        for series in decomposed.itervalues():
            self.assertListEqual(series.timestamps, [1, 2, 3, 4, 5])
        self.assertListEqual(decomposed['trend'].values, [150] * 5)
        self.assertListEqual(decomposed['seasonal'].values, [-50, 50, -50, 50, -50])
        self.assertListEqual(decomposed['residual'].values, [0] * 5)

    def test_accessors(self):
        foo = TimeSeries({ 1: 2, 3: 4 })
        bar = TimeSeries({ 5: 6, 7: 8 })
        group = TimeSeriesGroup(foo=foo, bar=bar)
        self.assertIs(foo, group['foo'])
        self.assertIs(bar, group['bar'])
        self.assertEquals(len(group), 2)
        del group['foo']
        self.assertEquals(len(group), 1)
        group['foo'] = foo
        self.assertEquals(len(group), 2)
        self.assertIs(foo, group['foo'])
        self.assertListEqual(group.items(), [ ('foo', foo), ('bar', bar) ])

    def test_linear_trend(self):
        foo = TimeSeries([ (1, 32), (2, 55), (3, 40) ])
        bar = TimeSeries([ (4, 42), (5, 65), (6, 50) ])
        group = TimeSeriesGroup(foo=foo, bar=bar)
        trend = group.trend()
        self.assertListEqual(trend['foo'].x, [1, 2, 3])
        self.assertListEqual(trend['foo'].y, [38, 42, 46])
        self.assertListEqual(trend['bar'].x, [4, 5, 6])
        self.assertListEqual(trend['bar'].y, [48, 52, 56])
