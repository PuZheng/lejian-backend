#! /usr/bin/env python
# -*- coding: UTF-8 -*-
from werkzeug.security import generate_password_hash
from path import path
import sh
import random
import string
from datetime import timedelta

from lejian.basemain import app
from lejian.tools.init_db import init_db
from lejian.tools.gen_roles import gen_roles
from lejian.models import User, SPU, Role, Vendor, SPUType, Retailer, SKU
from lejian.utils import do_commit, assert_dir
from lejian import chance


lorem = (
    'Omnis nesciunt sed debitis ad illum facere in exercitationem. Dolorum eum'
    'impedit sit nostrum porro quia laborum. Nesciunt temporibus voluptatum in '
    'nihil eum consequuntur. Aut porro nemo cupiditate aut nobis maxime.')

if __name__ == '__main__':
    init_db()
    roles = gen_roles()
    role_super_admin = [role for role in roles if role.name == '系统管理员'][0]

    print('create super admin ...')
    do_commit(User(role=role_super_admin, email='admin@lejian.com',
                   password=generate_password_hash('admin',
                                                   'pbkdf2:sha256')))

    print('create spu types ...')
    dir_ = assert_dir(path.joinpath(app.config['ASSETS_DIR'],
                                    'spu_type_pics'))
    spu_types = []
    for i in range(8):
        name = chance.word()
        spu_types.append(
            do_commit(SPUType(name=name,
                              enabled=True,
                              weight=random.randrange(0, 10),
                              pic_path=chance.image(dir_=dir_, text=name,
                                                    size=(480, 480))))
        )

    dir_ = path.joinpath(app.config['ASSETS_DIR'], 'spu_pics')
    sh.rm('-rf', dir_)
    assert_dir(dir_)

    vendor_role = Role.query.filter(Role.name == '厂商').one()
    for i in range(16):
        name = chance.word()
        print('create vendor ' + name + ' ...')
        admin = do_commit(User(role=vendor_role,
                               password=generate_password_hash(
                                   name, 'pbkdf2:sha256')))
        domain = chance.domain()
        vendor = do_commit(Vendor(
            name=name,
            telephone=chance.telephone(),
            address=chance.address(),
            email='support@' + domain,
            website='http://' + domain,
            weixin_number=chance.word(),
            weibo=chance.word(),
            weibo_link='http://weibo.com/u/' + chance.word(),
            brief=chance.lorem(),
            create_time=chance.time(),
            admin=admin))

        for i in range(random.randrange(1, 32)):
            spu = do_commit(SPU(name=chance.word(),
                                code=chance.word(string.digits),
                                vendor=vendor, msrp=random.randrange(1000,
                                                                     10000),
                                spu_type=random.choice(spu_types),
                                description=chance.lorem(),
                                rating=random.randrange(1, 6),
                                create_time=chance.time()))
            dir_ = assert_dir(path.joinpath(app.config['ASSETS_DIR'],
                                            'spu_pics',
                                            str(spu.id)))
            chance.image(dir_=dir_, filename='icon.jpg', size=(96, 96))
            chance.image(dir_=dir_, size=(480, 480))
            chance.image(dir_=dir_, size=(480, 480))
            chance.image(dir_=dir_, size=(480, 480))
            chance.image(dir_=dir_, size=(480, 480))

            skus = []
            for j in range(random.randrange(3000, 4000)):
                manufacture_date = chance.date([-365, -1])
                expire_date = manufacture_date + timedelta(
                    days=random.randrange(30, 3 * 365))
                skus.append(SKU(spu=spu,
                                last_verify_time=chance.time([-7 * 24 * 3600,
                                                              - 24 * 3600]),
                                manufacture_date=manufacture_date,
                                expire_date=expire_date,
                                token=chance.word(),
                                checksum=chance.word()))
            do_commit(skus)

    retailer_role = Role.query.filter(Role.name == '零售商').one()
    for i in range(random.randrange(1, 80)):
        name = chance.word()
        print('create retailer ' + name)
        admin = do_commit(User(role=retailer_role,
                               password=generate_password_hash(
                                   name, 'pbkdf2:sha256')))
        do_commit(Retailer(name=name,
                           brief=chance.lorem(),
                           rating=random.randrange(1, 6),
                           telephone=chance.telephone(),
                           address=chance.address(),
                           create_time=chance.time(),
                           admin=admin,
                           enabled=True,
                           **chance.lng_lat()))
