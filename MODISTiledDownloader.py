import os
import requests
from html.parser import HTMLParser

class Parser(HTMLParser):
    valid_links = []

    def __init__(self):
        HTMLParser.__init__(self)
        self.recording = False

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.recording = True

    def handle_endtag(self, tag):
        if tag == 'a':
            self.recording = False

    def handle_data(self, data):
        if self.recording:
            if data[-3:] == 'hdf':
                self.valid_links.append(data)


class SessionWithHeaderRedirection(requests.Session):
    AUTH_HOST = 'urs.earthdata.nasa.gov'

    def __init__(self, username, password):
        super().__init__()
        self.auth = (username, password)

    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url
        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)

            if (original_parsed.hostname != redirect_parsed.hostname) and \
                    redirect_parsed.hostname != self.AUTH_HOST and \
                    original_parsed.hostname != self.AUTH_HOST:
                del headers['Authorization']
        return

class MODISTiledDownloader():
    # product - e.g. MOD11A1
    def __init__(self, user, password, output_dir):
        self.user = user
        self.password = password
        self.session = SessionWithHeaderRedirection(user, password)
        self.output_dir = output_dir

    def product_to_baseurl(self, product):
        base_url = None
        if product[0:3] == 'MOD':
            base_url = 'https://e4ftl01.cr.usgs.gov/MOLT/%s.006' % product
        if product[0:3] == 'MYD':
            base_url = 'https://e4ftl01.cr.usgs.gov/MOLA/%s.006' % product
        if product[0:3] == 'MCD':
            base_url = 'https://e4ftl01.cr.usgs.gov/MOTA/%s.006' % product
        return base_url

    def download_product_for_date_and_tile(self, product, tile_date, tile_num):
        # tile_date - datetime object
        # tile_num - e.g. h20v03
        parser = Parser()
        parser.valid_links = []
        base_url = self.product_to_baseurl(product)
        if base_url == None:
            print ('Invalid product')
            return

        current_url = base_url + '/%s/' % tile_date.strftime('%Y.%m.%d')
        current_date_content = requests.get(current_url).content
        parser.feed(str(current_date_content))

        found = False
        for valid_link in parser.valid_links:
            if valid_link.split('.')[2] in [tile_num]:
                found = True
                approved_url = current_url + valid_link
                new_file_name = os.path.join(self.output_dir, valid_link)
                print('Downloading file to %s...' % new_file_name)

                response = self.session.get(approved_url, stream=True)
                response.raise_for_status()
                with open(new_file_name, 'wb') as fd:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        fd.write(chunk)
        if found == False:
            print ('No data found')
        parser.valid_links = []
