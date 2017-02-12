import ConfigParser
import cheez_cave.service.chart_service as chart_service

config = ConfigParser.ConfigParser()
config.read('/home/pi/cheez_cave/cheez_cave.conf')

chart = chart_service.ChartService(config)
chart.generate_xy_chart('test.svg')

