from MODISTiledDownloader import MODISTiledDownloader
from datetime import datetime, timedelta

username = 'YOUR_USERNAME'
password = 'YOUR_PASSWORD'
products = ['MOD11A2']
output_dir = '/'
start_date = datetime(2018, 1, 2)
end_date = datetime(2020, 2, 20)
tiles = ['h19v03']


downloader = MODISTiledDownloader(user=username,
                                  password=password,
                                  output_dir=output_dir)


current_date = start_date
while current_date <= end_date:
    print ('Processing day %s' % current_date.strftime('%Y.%m.%d'))
    for product in products:
        print ('Get product %s' % product)
        for tile in tiles:
            print('Get tile %s' % tile)
            downloader.download_product_for_date_and_tile(product, current_date, tile)