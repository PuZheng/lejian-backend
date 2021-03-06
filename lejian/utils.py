# -*- coding: UTF-8 -*-
import os
import types
from PIL import Image
import re
from flask import current_app
import urllib
import tempfile
import shutil
from path import path


def do_commit(obj, action="add"):
    from .database import db
    if action == "add":
        if isinstance(obj, list) or \
           isinstance(obj, tuple):
            db.session.add_all(obj)
        else:
            db.session.add(obj)
    elif action == "delete":
        db.session.delete(obj)
    db.session.commit()
    return obj


def as_dict(fields, d):
    items = []
    for field in fields:
        if isinstance(field, types.StringType):
            items.append((field, d.get(field)))
        elif isinstance(field, types.TupleType):
            items.append((field[0], d.get(field[1])))
    return dict(items)


def assert_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


# def get_or_404(cls, id_):
#     from .database import db
#     assert issubclass(cls, db.Model) or issubclass(cls, ModelWrapper)
#     return wraps(cls.query.get_or_404(id_))


def resize_and_crop(img_path, modified_path, size, crop_type='top'):
    """
    Resize and crop an image to fit the specified size.

    args:
        img_path: path for the image to resize.
        modified_path: path to store the modified image.
        size: `(width, height)` tuple.
        crop_type: can be 'top', 'middle' or 'bottom', depending on this
            value, the image will cropped getting the 'top/left', 'midle' or
            'bottom/rigth' of the image to fit the size.
    raises:
        Exception: if can not open the file in img_path of there is problems
            to save the image.
        ValueError: if an invalid `crop_type` is provided.
    """
    # If height is higher we resize vertically, if not we resize horizontally
    img = Image.open(img_path)
    # Get current and desired ratio for the images
    img_ratio = img.size[0] / float(img.size[1])
    ratio = size[0] / float(size[1])
    if ratio > img_ratio:
        img = img.resize((size[0], size[0] * img.size[1] / img.size[0]),
                         Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, img.size[0], size[1])
        elif crop_type == 'middle':
            box = (0, (img.size[1] - size[1]) / 2, img.size[0],
                   (img.size[1] + size[1]) / 2)
        elif crop_type == 'bottom':
            box = (0, img.size[1] - size[1], img.size[0], img.size[1])
        else:
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    elif ratio < img_ratio:
        img = img.resize((size[1] * img.size[0] / img.size[1], size[1]),
                         Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, size[0], img.size[1])
        elif crop_type == 'middle':
            box = ((img.size[0] - size[0]) / 2, 0, (img.size[0] + size[0]) / 2,
                   img.size[1])
        elif crop_type == 'bottom':
            box = (img.size[0] - size[0], 0, img.size[0], img.size[1])
        else:
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    else:
        img = img.resize((size[0], size[1]), Image.ANTIALIAS)
        # If the scale is the same, we do not need to crop
    img.save(modified_path)


def to_camel_case(arg):
    if isinstance(arg, dict):
        return dict((to_camel_case(k), v) for k, v in arg.items())
    assert isinstance(arg, str)
    return re.sub(r'_([a-z0-9])', lambda m: m.groups()[0].upper(), arg)


def snakeize(arg):
    if isinstance(arg, dict):
        return dict((snakeize(k), v) for k, v in arg.items())
    assert isinstance(arg, str)
    tmp = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', arg)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', tmp).lower()


def asset_url(path_):
    return urllib.parse.urljoin(current_app.config['SITE'], path_)


def formalize_temp_asset(dir_, path_):
    if path(path_).exists():
        _, ext = path(path_).splitext()
        new_path = tempfile.mktemp(suffix=ext, dir=dir_, prefix='')
        shutil.move(path_, new_path)
        return new_path
