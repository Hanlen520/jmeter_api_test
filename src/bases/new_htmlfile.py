# -*- coding: utf-8 -*-
# @Time    : 2018/8/23 11:42
# @Author  : Burrows
# @FileName: new_htmlfile.py

'''基础类，用于返回workplace路径下最新的ant_report_${newest}文件夹下的最新.html与.jtl文件'''

import os


class NewHtmlFile:
    def __init__(self):
        # 获取最新生成的 ant_report_${date-time} 文件夹
        global newest_workplace
        global conf_dir
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 项目根路径
        workplace_dir = root_dir + '/' + 'workplace'
        conf_dir = root_dir + '/' + 'conf'
        list_report = []
        for x in os.listdir(workplace_dir):
          if x.startswith("ant_report"):
            list_report.append(x)
        list_report.sort(key=lambda fn: os.path.getmtime(workplace_dir + '/' + fn))
        newest_workplace = workplace_dir + '/' + list_report[-1]
        self.testreport_dir = newest_workplace

    def get_newfile(self):
        '''
        :return:
            new_html_name : 新html文件名称，一般为test_report.html
            new_html_path : 新html文件路径
            new_jtl_name : 新jtl文件名称，一般为test_report.jtl
            new_jtl_path : 新jtl文件路径
        '''
        listtmp = os.listdir(self.testreport_dir)
        list_html = []
        list_jtl = []
        for x in listtmp:
            if x.endswith(".html"):
                list_html.append(x)
        for x in listtmp:
            if x.endswith(".jtl"):
                list_jtl.append(x)
        list_html.sort(key=lambda fn: os.path.getmtime(self.testreport_dir + '/' + fn))
        list_jtl.sort(key=lambda fn: os.path.getmtime(self.testreport_dir + '/' + fn))
        new_html_name = list_html[-1]
        new_jtl_name = list_jtl[-1]
        new_html_path = os.path.join(self.testreport_dir, list_html[-1])
        new_jtl_path = os.path.join(self.testreport_dir, list_jtl[-1])
        return new_html_name, new_html_path, new_jtl_name, new_jtl_path
