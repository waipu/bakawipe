# -*- coding: utf-8 -*-
# -*- mode: python -*-
import os
from subprocess import Popen

viewer_cmd = ['ida']


def hands_solve(ipath):
  vc = viewer_cmd[:]
  vc.append(ipath)
  viewer = Popen(vc)
  try:
    code = input('code:')
  finally:
    viewer.terminate()
    os.unlink(ipath)
  return code
