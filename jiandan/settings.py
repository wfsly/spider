# encoding: utf-8

import os

# os.path.dirname(__file__) get the directory name of current file
# ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
# 以当前文件夹为基准获取项目的绝对路径
ROOT_DIR = os.path.abspath('./')
PARENT_DIR = os.path.abspath('../')

IMAGE_DIR = os.path.join(ROOT_DIR, 'images/')

# === NEVER PUT MORE SETTINGS AFTER HERE ===
settings_local = os.path.join(ROOT_DIR, "settings_local.py")
if os.path.exists(settings_local):
    execfile(settings_local)

if __name__ == "__main__":
    print ROOT_DIR
    print PARENT_DIR
    print IMAGE_DIR
