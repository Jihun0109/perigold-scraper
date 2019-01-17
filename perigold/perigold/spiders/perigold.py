# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from urlparse import urlparse
import sys
import re, os, requests, urllib
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time
from shutil import copyfile
import json, re, os
from fake_useragent import UserAgent

ip_list = [
    '107.172.228.190:80',
    '154.16.55.211:80',
    '192.210.194.206:80',
    '104.140.83.23:80',    
    '107.158.141.122:80',
    '154.16.55.198:80',
    '154.16.55.215:80',
    '107.158.141.89:80',
    '155.94.134.253:80',
    '155.94.134.14:80',
    '104.140.83.111:80',
    '155.94.134.168:80',
    '104.140.83.22:80',
    '107.172.227.235:80',
    '206.41.185.126:80',
    '206.41.185.123:80',
    '172.245.25.79:80',
    '154.16.55.229:80',
    '107.172.228.176:80',
    '104.140.83.201:80',    
]

error_list = []

def download(url, destfilename):
    if not os.path.exists(destfilename):
        print "Downloading from {} to {}...".format(url, destfilename)
        try:
            hdr = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',                                       
                  }
            
            if destfilename.split(".")[-1].lower() != 'jpg':
                hdr = {}

            #for ip in ip_list:
            try:
                proxyDict = {
                    "http": "http://{}".format(ip),
                    "https": "https://{}".format(ip)
                }

                with requests.Session() as s:
                    r = s.get(url, stream=True, headers=hdr, proxies=proxyDict)
                    size = 0
                    
                    with open(destfilename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=2048):
                            if chunk:
                                size += len(chunk)
                                f.write(chunk)
                                f.flush()
                        print ">>> ", size, " bytes downloaded."
                    if size != 3271:
                        print "OK!!!"
                    else:
                        print "<<< Image Error."
                        error_list.append(url)
                    # if os.path.isfile(destfilename):
                    #     os.remove(destfilename)
            except:
                # if os.path.isfile(destfilename):
                #     os.remove(destfilename)
                #continue
                pass

            return True
        except:
            print "Error downloading file."
            return False
            
    else:
        print " !!!!!!  The file {} already exists !!!!!!".format(destfilename)
        return True

class PerigoldSpider(Spider):
    name = "perigold"
    start_urls = ['https://www.perigold.com/brand/bnd/aerin-home-b47918.html']

    brand_name = "AERIN"


    def start_requests(self):
    	for url in self.start_urls:
    		yield Request(url, self.parse)
            
    def parse2(self, response):
        brands = response.xpath('//*[@class="xltext centertext"]/a/@href').extract()
        for b in brands:
            url = response.urljoin(b)
            yield Request(url, self.parse_brands)
            

    def parse_brands(self, response):
        brands = response.xpath('//*[@id="brands_list"]/a')
        for b in brands:
            name = b.xpath('./text()').extract_first()
            link = b.xpath('./@href').extract_first()
            item = {
                'brand': name.encode('utf8'),
                'link': link
            }
            yield item

    def parse(self, response):
        ua = UserAgent()
        
        brand_index = re.findall('\-b([\d]+)', response.url)[0]
        print brand_index
        get_data_url = "https://www.perigold.com/a/manufacturer_browse/get_data?category_id=0&caid=0&maid={}&curpage=1".format(brand_index)

        print get_data_url

        headers = {
            'accept': 'application/json',            
            'x-requested-with': 'XMLHttpRequest'
        }

        yield Request(get_data_url, self.parse_products, headers=headers)

    def parse_products(self, response):
        print response.url
        jdata = json.loads(response.body)
        products = jdata['browse']['browse_grid_objects']
        product_count = jdata['browse']['product_count']
        current_page = jdata['browse']['current_page']
        print len(products)
        print product_count
        print current_page

        for p in products:
            link = p['url']
            #link = "https://www.perigold.com/home/pdp/aerin-300-piece-shagreen-poker-set-aerh1231.html"
            #link = "https://www.perigold.com/tabletop-kitchen/pdp/aerin-coral-bottle-stopper-aerh1035.html"
            yield Request(link, self.parse_product)
            

        if product_count > current_page * 48:
            url = response.url.split("curpage=")[0] + "curpage=" + str(current_page+1)
            headers = {
                'accept': 'application/json',            
                'x-requested-with': 'XMLHttpRequest'
            }
            yield Request(url, self.parse_products, headers=headers)

    def parse_product(self, response):

        collections = ['acton', 'asher', 'ashton','audio','axel','caprice','christian','christina',
                        'concord','david','dean','duncan','faux','flex','haley','heinrich','henderson','howden',
                        'jane','jesse','joseph','linwood','lukas','marana','markus','max','milo','montgomery','paige',
                        'pierre','salazar','solomon','valentina','windham','woolbrook',
                        'celeste','double','driftwood','front','ignite','lincoln','plug','prism','wall']
        item = OrderedDict()
        
        base_title = response.xpath('//meta[@property="og:title"]/@content').extract_first()

        custom_description = ''
        
        dimension_str = ''
        swatch_colors = {}
        property_divs = response.xpath('//div[@class="panel-group"]/div')
        schematic_image = None
        pdf_link = None
        # self.brand_name = response.meta['brand']

        designer = ''#''.join(response.xpath('//*[text()="Features:"]/following-sibling::ul//li[contains(text(),"Design")]/text()').extract())
        if designer != '':
            designer = designer.split(":")[-1].split("/")[0]

        modelno = ''

        if designer != '' :
            title = self.brand_name +' ' + base_title + ' by ' + designer + ' - ' + modelno + ' - Welivv.com'
        else:
            title = self.brand_name +' ' + base_title + ' - Welivv.com'

        item['src'] = response.url
        item['custom_title'] = title

        modelnos = [modelno]

        title = base_title.replace('&reg;','').replace('&trade;','').replace('&eacute;','e').replace('&amp;','').replace('&quot;','')
        
        title = title.replace(', Set of 2','').replace('Big Bang','Bigbang').replace('Diesel Collection','DieselCollection').replace('Le Soleil','LeSoleil').\
                replace('New Buds','Newbuds')

        temp_id = self.brand_name.lower().replace(' ', '') + ' '+title.lower().replace('-','').replace('.','').replace('\'','').replace('/',' ').\
                        replace('&ucirc;','u').replace('spun light','spunlight').replace('string light','stringlight').replace('miss k','missk').replace('top top','toptop')


        temp_id = temp_id.replace('floor lamp','floorlamp').replace('desk lamp','desklamp').replace('table lamp', 'tablelamp').\
                    replace('pendant light','pendantlight').replace('desk light','desklight').replace('wall light', 'walllight').replace('wall sconce', 'wallsconce').\
                    replace('path light','pathlight').replace('ceiling light', 'ceilinglight').replace('recessed light','recessedlight').replace('gift set','giftset').\
                    replace('suspension light','suspensionlight').replace('wall lamp','walllamp').replace('ceiling lamp','ceilinglamp').replace('pendant lamp','pendantlamp').\
                    replace('seat pad','seatpad').replace('pedestal fan','pedestalfan').replace('ceiling fan','ceilingfan').replace('wall control','wallcontrol').\
                    replace('remote control','remotecontrol').replace('caster set','casterset').replace('side table','sidetable').replace('chair set','chairset').\
                    replace('bath bar','bathbar').replace('flush mount','flushmount').replace('suspension system','suspensionsystem').\
                    replace('lighting system','lightingsystem').replace('hanger kit','hangerkit').replace('bath light','bathlight').replace('dining chair','diningchair').\
                    replace('vanity light','vanitylight').replace('mirror kit','mirrorkit').replace('suspension lamp','suspensionlamp').replace('coffee table','coffeetable').\
                    replace('dining table','diningtable')

        # temp code start
        # yield item
        # return
        # temp code end

        words = temp_id.lower().split(' ')

        id = self.brand_name.lower().replace(' ', '') +'-' + ''.join(words[1:-1]) + '-' + words[-1]

        collection_temp = ' '.join(response.xpath('//div[contains(text(),"This Collection")]/following-sibling::*[1]/text()').extract())
        collection = collection_temp.split(' by ')[0]

        if collection:
            collection = collection.lower()
            id = id.replace(collection+"-",'')
            collection = collection.replace(' ','')
            id = id + "-" + collection

        id = id.replace('(', '').replace(')', '').replace(',', '').replace(':', '').replace('\"', '').replace(u'é',u'e')
        # ID Exception process
        item['sku'] = id        

        item['modelno'] = modelno#response.xpath('//*[@class="ellipsis"]/text()').extract_first().strip()
        item['available_new'] = "1-2 Weeks"
        item['sale_price'] = ''
        item['call_price'] = ''
        original_price = response.xpath('//*[contains(@class, "BasePriceBlock--list")]/text()').re('[\d.,]+')
        price = ''
        if original_price:
        	price = original_price[0]
        else:
        	price = response.xpath('//*[@class="BasePriceBlock"]/text()').re('[\d.,]+')[0].replace(',','')

        item['price'] = price
        item['pbrand:custom'] = self.brand_name

        swatches = {}
        ### Color options ###
        cccolor = response.xpath('//*[contains(@aria-label,"Select Color")]/option[2]/text()').extract()
        print "##############"
        print cccolor
        if not cccolor:
        	cccolor = response.xpath('//td[contains(text(), "Color") and not(contains(text(), "Color Temperature"))]/following-sibling::td[1]/text()').extract()	


        item['pcolor_new'] = [cccolor[0]] if cccolor else []

        attributesKey = {}
        options_keys = []
             
        vvvvoltage = response.xpath('//td[contains(text(), "Voltage")]/following-sibling::td[1]/text()').re('[\d.]+')
        item['voltage'] = vvvvoltage[0] if vvvvoltage else ''
        bbbultype = response.xpath('//td[contains(text(), "Bulb Type")]/following-sibling::td[1]/text()').extract()
        item['bulb'] = bbbultype[0] if bbbultype else ''

        ### Dimensions ###
        item['width'] = ""
        item['height'] = ""
        item['diameter'] = ""
        item['depth'] = ""

        display_dimensions = "<div>";

        dimensions_temps = response.xpath('//*[@class="ProductWeightsDimensions"]//dt[not(contains(text(), "Weight"))]')
        
        for iii, dm in enumerate(dimensions_temps):
            display_dimensions += "<li>"
            dd = ' '.join(dm.xpath('./following-sibling::dd[1]//text()').extract())
            if iii != 0:
            	display_dimensions += dm.xpath('./text()').extract_first()+": "

            display_dimensions += dd
            display_dimensions += "</li>"            
        
        display_dimensions += "</div>"

        width = re.findall('([\d.,\"]+)\'\'\s*W', display_dimensions)
        if width:
            item['width'] = width[0].replace('"','').strip('\n')
        height = re.findall('([\d.,\"]+)\'\'\s*H', display_dimensions)
        if height:
            item['height'] = height[0].replace('"','').strip('\n')
        depth = re.findall('([\d.,\"]+)\'\'\s*D', display_dimensions)
        if depth:
            item['depth'] = depth[0].replace('"','').strip('\n')

        item['display_dimensions'] = display_dimensions

        item['options'] = ""
        item['manauall_flag'] = ''       

        item['modelno'] = modelno
        item['designer'] = ""

        manufacture = ''.join(response.xpath('//*[text()="Features:"]/following-sibling::ul//li[contains(text(),"Manufacture")]/text()').extract()).split(":")[-1]
        if manufacture == '':
            manufacture = ''.join(response.xpath('//*[text()="Features:"]/following-sibling::ul//li[contains(text(),"Made in")]/text()').extract()).split("Made in")[-1]

        item['mss_made_in'] = response.xpath('//td[contains(text(), "Country")]/following-sibling::td[1]/text()').extract_first()
        item['brandlink'] = self.brand_name
        item['designer_link'] = ""
        item['modelnos'] = modelnos

        item['shape'] = ''
        item['qualifications'] = ''
        item['related_items'] = ''
        item['tags'] = ''
        item['notes'] = ''
        item['warranty'] = '"1 Year"'
        item['prioritization'] = ''
        item['categories'] = ' / '.join(response.xpath('//*[@class="Breadcrumbs-listItem"]/a/text()').extract())
        #item['product-categories'] = ''
        item['product_type_filters'] = ''
        item['collection_placement:custom'] = ''
        if collection:
            item['collection_placement:custom'] = self.brand_name.lower().replace(' ', '') + "-"+collection
        item['expiration_date'] = ''

        item['pdfs'] = []

        pdfs = response.xpath('//a[contains(@href, ".pdf")]/@href').extract()
       
            #http://www.electricfireplacesdirect.com
        if pdfs:
            pdf_path = "resource/{}/PDF/".format(self.brand_name)
            if not os.path.exists(pdf_path):
                os.makedirs(pdf_path)

            pdfs = list(set(pdfs))
            iii = 1
            pdf_files = []
            
            for idx, pdf in enumerate(pdfs):
                filename = id + "-pdf" + str(iii) + ".pdf"
                res = download(response.urljoin(pdf), pdf_path+filename)
                iii += 1
                if res:                    
                    pdf_files.append(filename)
            item["pdfs"] = pdf_files


        # IMAGE
        # images_list_temp = response.xpath('//*[@class="s7thumb"]/@style').extract()
        images = []

        schematic_images = []


        images = response.xpath('//li[contains(@class,"ProductDetailImage")]//img/@src').extract()

        img_files = [];
        for idx, image in enumerate(images):
            
            image_path = "resource/{}/Images/".format(self.brand_name)
            #image = image.replace("-fg","-ag")
            image = image.replace("resize-h60-w60","resize-h800")

            print "Converting from \"",image,"\""
            d,u = image.split("/im/")
            k,i = u.split("/resize")

            image = d + "/im/" + str(int(k)+10) + "/resize" + i
            print "to \"", image ,"\""

            if not os.path.exists(image_path):
                os.makedirs(image_path)

            extension = 'jpg'
            filename = id
            if idx > 0:
                filename = filename + "-image{}".format(idx)
            #item[key] = filename
            img_files.append(filename)

            filename = filename + "." + extension
            final_image = image
            download(response.urljoin(image), image_path+filename)

        item["images"] = img_files

        

        schematic_image = response.xpath('//*[@class="dim-con mt2"]/amp-img/@src').extract_first()

        item['installations'] = "https://s3.amazonaws.com/welivv/magento/schematics/" + id+'-schematic' + ".jpg"
        schematic_path = "dimplex_all/{}/Schematics/".format(self.brand_name)

        if schematic_image:
            dest_file = schematic_path+id+'-schematic'+".jpg"
            if not os.path.exists(dest_file):
                download(response.urljoin(schematic_image), dest_file)

        
        item['color_images'] = ""

        custom_description = ''.join(response.xpath('//*[@class="ProductOverviewInformation-description"]/text()').extract())
        # item['pcolor'] = ''
        item['name'] = base_title
        caption = '<b>{} '.format(self.brand_name) + title + '</b><br>'
        item['caption'] = caption
        item['custom_description'] = custom_description.strip('\n').strip()
        item['custom_keyword'] = self.brand_name.lower() + ',' + ','.join(title.split(',')[0].replace('/',' ').lower().split(' '))
        item['custom_headline'] = base_title

        

        item['finish_new'] = ''

        item['code'] = ''

        brand = self.brand_name

        title = item['modelno'] + ' ' + brand

        # if 'by' in title:
        #     title = title.split('by')[0]
        #
        # else:w
        #     title = self.ups_list[key]['title'].split('-')[0]
        # title = title.replace('  ', '+').replace(' ', '+').lower().replace('outdoor', '')
            # https://www.google.com/search?biw=907&bih=944&tbm=shop&ei=j8LgWoPhEoKsjwPL4bTABg&q=Anemone+Large+Wall+Ceiling+Light&oq=Anemone+Large+Wall+Ceiling+Light

        raw_html = response.xpath('//script[contains(text(), "csrfToken")]/text()').extract_first()
        raw_jdata = re.findall('wf.extend\((.*\}\})\);', raw_html)

        swatch_images = {}
        colors = []

        if raw_jdata:
        	jdata = json.loads(raw_jdata[0])
        	d1 = jdata['wf']['reactData']
        	if d1:
        		for key in d1.keys():
        			try:
        				d2 = d1[key]['bootstrap_data']['options']['standardOptions']

        				if len(d2) > 0:
        					full_options = []
        					for opt in d2:
        						options_sub = ""
        						opt_name = opt['category_name']
        						options = opt['options']
        						options_sub += '"' + opt_name + '":['
        						oo = []
        						for o in options:
        							ostr = '"' + o['name']
        							if int(o['cost']) > 0:
        								ostr += '(+$' + str(o['cost']) + ')'
        							ostr += '"'
        							oo.append(ostr)
        							if "Color" in opt_name or "Finish" in opt_name:
        								colors.append(o['name'])

        							#append swatch
        							if "swatch_option_thumbnail" in o.keys():
        								kkk = item['sku']+'-'+o['name'].lower().replace(' ','').replace('/','') + ":" + o['name']
        								swatch_images[kkk] = o['swatch_option_thumbnail']

        						options_sub += ','.join(oo)
        						options_sub += ']'
        						full_options.append(options_sub)

        					item['options'] = '{' + ','.join(full_options) +'}'
        					break
        			except:        				
        				continue

        if len(swatch_images.keys()) > 0:
            item['color_images'] = swatch_images.keys()
            for swch in swatch_images.keys():
                image_path = "resource/{}/Swatches/".format(self.brand_name)
                if not os.path.exists(image_path):
                    os.makedirs(image_path)
                extension = 'jpg'
                filename = swch.split(":")[0]
                filename = filename + "." + extension
                download(swatch_images[swch], image_path+filename)

        if colors:
        	item['pcolor_new'] = list(set(item['pcolor_new'] + colors))
        	
        print "ERRORLIST ", error_list
        yield item
        

    def errGoogle(self, response):
        yield response.request.meta['item']
    def parse_upc(self, response):
        url = response.xpath('//*[@class="sh-dgr__thumbnail"]/a/@href').extract()
        if not url:
            url = response.xpath('//*[@class="sh-dlr__thumbnail"]/a/@href').extract()
        if not url:
            yield response.meta['item']
        else:
            for i, item_url in enumerate(url):
                if i > 0: break
                if 'shopping/product' in item_url:
                    yield Request(response.urljoin(item_url), callback= self.parse_upc_final, meta={'item': response.meta['item']})
                else:
                    yield Request(response.urljoin(item_url), callback= self.parse_upc_final, meta={'item': response.meta['item']})

    def parse_upc_final(self, response):
        item = response.meta['item']
        specs = response.xpath('//*[@id="specs"]//div[@class="l7AxXb"]')
        flag = False
        brand = ''
        for spec in specs:
            try:
                key = spec.xpath('./span[@class="xBLOLc"]/text()').extract_first()

                val = spec.xpath('./span[@class="gaBVed"]/text()').extract_first()

                if key == 'Part Numbers' or key == 'Part Number':
                    models = val.split(',')
                    for model in models:
                        if item['modelno'] in model.replace(' ','').strip() or model.replace(' ','').strip() in item['modelno']:
                            # if brand !='' and brand[:3].lower() == item['title'].split(' ')[0][:3].lower():
                            flag = True
                elif key == 'GTIN':
                    # item['price'] = response.xpath('//span[@class="price"]/text()').extract_first().replace('$', '').replace(',', '')
                    item['code'] = val

                    # yield item
                elif key == 'Brand':
                    brand = spec.xpath('./span[@class="gaBVed"]/text()').extract_first().strip()

                    if brand !='' and brand[:3].lower() == item['pbrand:custom'].split(' ')[0][:3].lower():
                        flag = True
            except:
                continue
        self.count += 1
        print(self.count)
        yield item

    def getVariationPrices(self, varations, options_keys, lowest_price):

        lowest_int = float(lowest_price)
        intial_product = None
        initial_list = []
        # self.varations = varations

        for vari in varations:
            
            try:
            	product_price = float(vari['pricing']['sale'])
            except:
            	product_price = float(vari['pricing']['standard'])
            		
            diff = abs(product_price - lowest_int)
            if diff < 1:
                initial_list.append(vari)
                self.addVariation(vari, options_keys)

        # firstlist = initial_list
        self.nextlist = []
        self.getOneMatch(varations, initial_list)

        while True:
            if len(self.nextlist) > 0:
                firstlist = self.nextlist
                self.nextlist = []
                self.getOneMatch(varations, firstlist)
                print len(self.nextlist)
            else:
                break


    def addVariation(self, variation, options_keys, addedPrice=None):
        variations_list = variation['attributes'].keys()
        variations_list.sort()
        for attr_key in variation['attributes'].keys():
            varition = variation['attributes'][attr_key]
            indx = variations_list.index(attr_key)
            datas = self.total_options[options_keys[indx]]
            if not varition in datas:
                self.total_options[options_keys[indx]].append(varition)
                if addedPrice:
                    self.total_options_temp[options_keys[indx]].append(varition + '(+${})'.format(addedPrice))
                else:
                    self.total_options_temp[options_keys[indx]].append(varition)


    def getOneMatch(self, parent_list, param_list):
        # self.nextlist = []
        for param in param_list:
            for vari in parent_list:
                try:
                    parent_price = float(vari['pricing']['sale'])
                except:
                    parent_price = float(vari['pricing']['standard'])
                try:
                    param_price = float(param['pricing']['sale'])
                except:
                    param_price = float(param['pricing']['standard'])

                if parent_price <= param_price:
                    continue

                one_flag = False
                checked = False
                for attr_key in vari['attributes'].keys():
                    parent_vari = vari['attributes'][attr_key]
                    param_vari = param['attributes'][attr_key]
                    if parent_vari != param_vari and not one_flag:
                        one_flag = True

                        variations_list = vari['attributes'].keys()
                        variations_list.sort()
                        index = variations_list.index(attr_key)
                        datas = self.total_options[self.options_keys[index]]
                        if not parent_vari in datas:
                            checked = True
                    elif parent_vari != param_vari and one_flag:
                        checked = False
                        break

                if checked:
                    self.addVariation(vari, self.options_keys, parent_price-param_price)
                    self.nextlist.append(vari)

        # yield self.nextlist

    def get_category(self, old):
        print "######################################",old
        categories = {
            'Bathroom Accent Furniture':'Bath/Accent Furniture',
            'Bathtubs':'Bath/Bathtubs',
            'Bathtub Faucets':'/Faucets',
            'Sink Faucets':'Bath/Faucets',
            'Shower Trims':'Bath/Shower Trims',
            'Bathroom Showers':'Bath/Showers',
            'Shower-Tub':'Bath/Showers',
            'Bathroom Sinks':'Bath/Sinks',
            'Bathroom Storage':'Furniture  Bath/Storage',
            'Toilets + Bidets':'Bath/Toilets and Bidets',
            'Vanities':'Bath/Vanities',
            'Audio':'Decor/Audio',
            'Bathroom Accessories':'Decor/Bathroom Accessories',
            'Dinnerware ':'Decor/Dinnerware',
            'Drinkware':'Decor/Drinkware and Barware',
            'Decorative Home Accessories':'Decor/Home Accessories',
            'Office Accessories':'Decor/Office Accessories',
            'Housekeeping Tools + Supplies':'Furniture/Accessories',
            'Home Organization':'Furniture/Accessories/Home Organization',
            'Kids DÃ©cor + Accessories':'Furniture/Accessories/Kids',
            'Accent Pillows':'Furniture/Accessories/Pillows',
            'Rugs':'Furniture/Accessories/Rugs',
            'Privacy Screens + Room Dividers':'Furniture/Accessories/Screens and Dividers',
            'Throws + Blankets':'Furniture/Accessories/Throws and Blankets',
            'Beds':'Furniture/Beds',
            'Dressers + Armoires':'Furniture/Dressers',
            'Kids + Baby Furniture':'Furniture/Kids Furniture',
            'Kids Play':'Furniture/Kids Furniture',
            'Bath Mirrors':'Furniture/Mirrors',
            'Nightstands + Bedside Tables':'Furniture/Nightstands',
            'Benches':'Furniture/Seating/Benches',
            'Dining Armchairs':'Furniture/Seating/Chairs/Dining Arm Chairs',
            'Lounge Chairs':'Furniture/Seating/Chairs/Lounge Chairs',
            'Office Chairs':'Furniture/Seating/Chairs/Office Chairs',
            'Living Room Rocking Chairs + Gliders':'Furniture/Seating/Chairs/Rocking Chairs',
            'Dining Side Chairs':'Furniture/Seating/Chairs/Side Dining Chairs',
            'Ottomans, Poufs, Low Stools + Bean Bags':'Furniture/Seating/Ottomans',
            'Low Stools + Bean Bags':'Furniture/Seating/Ottomans, Poufs, and Bean Bags',
            'Ottomans + Poufs':'Furniture/Seating/Ottomans, Poufs, and Bean Bags',
            'Outdoor Seating':'Furniture/Seating/Outdoor Seating',
            'Sofas':'Furniture/Seating/Sofas and Sectionals',

            'Bar + Counter Stools':'Furniture/Seating/Stools',
            'Bar Stools + Counter Stools':'Furniture/Seating/Stools',
            'Living Room Storage + Organization':'Furniture/Storage & Shelving',
            'Dining Room Storage + Organization':'Furniture/Storage & Shelving/Dining Room Storage',
            'Medicine Cabinets':'Furniture/Storage & Shelving/Medicine Cabinets',
            'Office Storage':'Furniture/Storage & Shelving/Office Storage',
            'Desks':'Furniture/Storage and Shelving/Desks',
            'Buffets + Sideboards':'Furniture/Storage and Shelving/Sidebrards',
            'Coffee + Side Tables':'Furniture/Tables/Coffee Tables',
            'Living Room Tables':'Furniture/Tables/Coffee Tables',
            'Office Desks + Tables':'Furniture/Tables/Desks',
            'Dining Tables':'Furniture/Tables/Dining Tables',
            'Outdoor Tables':'Furniture/Tables/Outdoor Tables',
            'Tabletop':'Furniture/Tables/Table Tops',
            'Accent Lights':'Lighting/Accent Lighting',
            'Cabinet Lighting':'Lighting/Accent Lighting/Cabinet Lights',
            'Display Lighting':'Lighting/Accent Lighting/Picture Lights',
            'Deck + Step Lights':'Lighting/Accent Lighting/Step Lights',
            'Lighting Accessories':'Lighting/Accessories',
            'Bathroom Parts + Components':'Lighting/Accessories/Bath Accessories',
            'Linear Suspension':'Lighting/Ceiling Mounted Lights/Linear Suspension Lights',
            'Linear Suspension Lights':'Lighting/Ceiling Mounted Lights/Linear Suspension Lights',
            'Pendant Lights':'Lighting/Ceiling Mounted Lights/Pendant Lights',
            'Flush Mount Ceiling Lights':'Lighting/Ceiling Mounted Ligts/Ceiling Flush Lights',
            'Pendants':'Lighting/Ceiling Mounted Ligts/Pendants',
            'Semi-Flush Mount Ceiling Lights':'Lighting/Ceiling Mounted Ligts/Semi-Flush Lights',
            'Chandelier':'Lighting/Chandeliers',
            'Chandeliers':'Lighting/Chandeliers',
            'Ceiling Fans':'Lighting/Fans/Ceiling Fans',
            'Fans with Remotes':'Lighting/Fans/Ceiling Fans',
            'Wall Fans':'Lighting/Fans/Wall Fans',
            'Floor Lamps':'Lighting/Floor Lamps',
            'Landscape Lighting':'Lighting/Outdoor Lighting/Landscape Lighting/Step Lights',
            'Recessed Lighting':'Lighting/Recessed Lighting',
            'Desk Lamps':'Lighting/Table & Desk Lamps/Desk Lamps',
            'Table Lamps':'Lighting/Table & Desk Lamps/Table Lamps',
            'Cable Lighting':'Lighting/Track & Rail Lighting/All Cable Lighting',
            'Monorail Lighting':'Lighting/Track & Rail Lighting/All Rail Lighting',
            'Track Lighting':'Lighting/Track & Rail Lighting/All Track Lighting',
            'Wall Lights':'Lighting/Wall Lights',
            'Bathroom Wall Lights':'Lighting/Wall Lights/Bath Vanity Lights',
            'Wall Sconces':'Lighting/Wall Lights/Sconces',
            'Outdoor Garden':'Outdoor/Garden',
            'Outdoor Textiles':'Outdoor/Outdoor Accessories',
            'Outdoor Lighting':'Outdoor/Outdoor Lighting',
            'Outdoor Storage':'/Storage',

        }

        try:
            if categories[old]:
                print categories[old]
                return categories[old]
            else:
                print "err"
                return old
        except:
            return old
