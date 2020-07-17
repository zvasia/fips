# -*- coding: utf-8 -*-

import itertools
import os
import re
import ssl

from datetime import datetime
from venv import logger

from googletrans import Translator
from scrapy.exceptions import DropItem
from six.moves.urllib.request import urlopen
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from .model import Certificate, Pics, ICGS
from .settings import UPDATE_IMAGES


class FipsAlchemyPipelibe(object):
    # ssl verification workaround
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    def open_spider(self, spider):
        self.fields_to_check = spider.settings['FIELDS_TO_UPDATE']
        self.dbengine = create_engine(spider.settings['SQLALCHEMY_DB'], encoding='utf-8', echo=True)
        Session = sessionmaker(bind=self.dbengine)
        self.session = Session()
        self.translator = Translator()
        os_id_start = self.session.query(func.max(Certificate.os_id).label("max_os_id")).scalar()
        self.num_gen = itertools.count((os_id_start or 0) + 1)

    def create_image(self, cert, item):
            pic = Pics(cert=cert.os_id)
            image_url = item['image_url']
            if image_url.startswith('/'):
                image_url = 'http://www1.fips.ru' + image_url
            pic.image = urlopen(image_url).read()
            self.session.add(pic)

    def check_fields(self, cert, item):
        if 'country' in item and cert.country != item['country']:
            cert.country = item['country']
            logger.info('"Country" was updated')

        if 'application_number' in item and cert.application_number != item['application_number']:
            cert.application_number = item['application_number']
            logger.info('"Application" number was updated')

        if 'valid_until' in item and cert.valid_until != datetime.strptime(item['valid_until'], "%d.%m.%Y").date():
            cert.valid_until = datetime.strptime(item['valid_until'], "%d.%m.%Y").date()
            logger.info('"Valid until" was updated')

        if 'application_date' in item and \
                cert.application_date != datetime.strptime(item['application_date'], "%d.%m.%Y").date():
            cert.application_date = datetime.strptime(item['application_date'], "%d.%m.%Y").date()
            logger.info('"Application date" was updated')

        if 'registration_date' in item and \
                cert.registration_date != datetime.strptime(item['registration_date'], "%d.%m.%Y").date():
            cert.registration_date = datetime.strptime(item['registration_date'], "%d.%m.%Y").date()
            logger.info('"Registration date" was updated to {}'.format(cert.registration_date))

        if "status_str" in item:
            parts = re.split('[:()]', item["status_str"])
            if parts[0].strip() == "Статус":
                status = parts[1].strip()
                status = status[0].upper() + status[1:]
                if cert.status != status:
                    cert.status = status
                    logger.info('"Status" was updated')

            if len(parts) > 2 and "последнее изменение" in parts[2]:
                status_date = datetime.strptime(parts[3].strip(), "%d.%m.%Y")
                if cert.status_date != status_date:
                    cert.status_date = status_date
                    logger.info('"Status date" was updated')

        if 'owner' in item and cert.owner != item['owner']:
            cert.owner = item['owner']
            logger.info('"Owner" was updated')

        if 'owner_address' in item and cert.owner_address != item['owner_address']:
            cert.owner_address = item['owner_address']
            logger.info('"Owner" was updated')

        if 'colors' in item and cert.colors != item['colors']:
            cert.colors = item['colors']
            logger.info('"Colours" was updated')

        if "priority" in item and cert.priority != datetime.strptime(item['priority'], "%d.%m.%Y").date():
            cert.priority = datetime.strptime(item['priority'], "%d.%m.%Y").date()
            logger.info('"Priority" was updated')

        if "icgs" in item:
            icgs = self.session.query(ICGS).filter_by(cert=cert.os_id)
            if icgs.count() > 0:
                logger.info('ICGS for certificate {} already exists'.format(cert.full_num))
                self.session.query(ICGS).filter_by(cert=cert.os_id).delete()
                self.session.commit()
                logger.info('Delete old ICGS and create new.')
            # create new icgs
            icgs_list = item["icgs"] if isinstance(item["icgs"], list) else [item["icgs"]]
            for icgs_str in icgs_list:
                icgs_parts = re.split('(\d+\s+-)', icgs_str)[1:]  # Cut the part before the first number
                for icgs_code, icgs_desc in zip(icgs_parts[::2], icgs_parts[1::2]):
                    icgs_code = int(icgs_code.strip('\t\n- '))
                    icgs_desc = icgs_desc.strip('\t\n; ')
                    try:
                        icgs_desc_en = self.translator.translate(icgs_desc, dest='en').text
                    except (IOError, ValueError):
                        icgs_desc_en = icgs_desc
                    icgs = ICGS(cert=cert.os_id, cls=icgs_code, descr_ru=icgs_desc, descr_en=icgs_desc_en)
                    self.session.add(icgs)
                    logger.info('ICGS was updated')

        if "image_url" in item:
            pics = self.session.query(Pics).filter_by(cert=cert.os_id)
            if pics.count() > 0:
                logger.error('Picture for certificate {} already exists'.format(cert.full_num))
                if UPDATE_IMAGES:
                    self.session.query(Pics).filter_by(cert=cert.os_id).delete()
                    self.session.commit()
                    logger.info('Old image was deleted')
                    self.create_image(cert, item)
                    logger.info('Image was uploaded')
            else:
                self.create_image(cert, item)
                logger.info('Image was uploaded')

        cert.update_date = datetime.utcnow()
        return cert

    def process_item(self, item, spider):
        full_num = item['number']
        item_type = item['type']
        if item_type is not 'TM':
            logger.warning('Doctype of {} is not "TM"'.format(full_num))
            raise DropItem
        # check if cert already exist
        try:
            cert = self.session.query(Certificate).filter_by(full_num=full_num, type=item_type)[0]
            logger.info('Found certificate with {} number. Trying to update fields.'.format(full_num))
            self.check_fields(cert, item)
        except IndexError:
            logger.info('No certificate with {} number. Trying to create new.'.format(full_num))
            num = int(full_num.split('/')[0])
            cert = Certificate(num=num, full_num=full_num, os_id=next(self.num_gen), type='TM', b900=num * 100)
            cert = self.check_fields(cert, item)
            cert.create_date = cert.update_date
            self.session.add(cert)
        finally:
            return item



    def close_spider(self, spider):
        spider.logger.info(f'TOTAL: {spider.requests_total}')
        spider.logger.info(f'INVALID DATA RECEIVED: {spider.requests_invalid_data}')
        spider.logger.info(f'INVALID DATA DOCNUMS: {str(spider.requests_invalid_docnums)}')
        spider.logger.info(f'TOTAL SUCCESS: {spider.requests_success}')
        self.session.commit()
