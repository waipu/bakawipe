# -*- coding: utf-8 -*-
# -*- mode: python -*-
import os

def get_img(net, url):
  img = net.req(url)
  return img

def save_img(fobj, fpath, tmppath='temp'):
  ipath = os.path.join(tmppath, fpath)
  ipath = ipath.rstrip('/')
  if not os.path.isfile(ipath):
    dpath = os.path.dirname(ipath)
    if not os.path.isdir(dpath):
      os.makedirs(dpath)
    with open(ipath, 'wb') as f:
      f.write(fobj)
  return ipath

def download_img(net, url, tmppath='temp'):
  img = get_img(net, url)
  return save_img(img, url.partition('://')[2], tmppath)
