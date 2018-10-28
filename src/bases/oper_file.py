# -*- coding: utf-8 -*-
# @Time    : 2018/6/16 10:48
# @Author  : Burrows
# @FileName: oper_file.py

"""基础类，封装操作文件的方法"""
import shutil


class OperFile:
    def copy_file(self, src, dst):
        """复制文件"""
        shutil.copyfile(src, dst)

    def trunc_file(self, filename):
        """清空文件"""
        with open(filename, 'w') as fp:
            fp.truncate()
