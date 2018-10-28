# -*- coding: utf-8 -*-
# @Time    : 2018/6/11 17:19
# @Author  : Burrows
# @FileName: make_report.py

"""基础类，封装生成excel报告的操作"""
import xlsxwriter
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bases.read_logger import ReadLogger

class Report:
    def __init__(self, report_name=None):
        # 获取logger和run_log
        read_logger = ReadLogger()
        self.logger = read_logger.get_logger()
        self.run_log_src = read_logger.get_run_log()

        if report_name is None:
            self.report_name = 'test_report_static.xlsx'
        else:
            self.report_name = report_name
        self.workbook = xlsxwriter.Workbook(self.report_name)
        self.worksheet = self.workbook.add_worksheet("测试总况")

        self.logger.info('生成测试报告: %s' % self.report_name)

    def close(self):
        self.workbook.close()

    # 设置写入格式
    def get_format(self, wd, option={}):
        return wd.add_format(option)

    # 返回excel路径
    def get_file(self):
        return self.report_name

    # 设置居中格式
    def get_format_center(self, wd, num=1):
        return wd.add_format({'align': 'center', 'valign': 'vcenter', 'border': num})

    # 写数据-根据坐标
    def _write_center(self, worksheet, cl, data):
        wd = self.workbook
        return worksheet.write(cl, data, self.get_format_center(wd))

    def init_data(self):
        """初始化表格"""
        self.logger.info('开始初始化测试报告数据....')
        # 设置sheet1列和行的宽高
        self.worksheet.set_column("A:A", 20)
        self.worksheet.set_column("B:B", 20)
        self.worksheet.set_column("C:C", 20)
        self.worksheet.set_column("D:D", 20)
        self.worksheet.set_column("E:E", 20)
        self.worksheet.set_column("F:F", 20)
        #self.worksheet.set_column("G:F", 20)

        self.worksheet.set_row(1, 30)
        self.worksheet.set_row(2, 30)
        self.worksheet.set_row(3, 30)
        self.worksheet.set_row(4, 30)
        self.worksheet.set_row(5, 30)
        self.worksheet.set_row(6, 30)
        self.worksheet.set_row(7, 30)
        self.worksheet.set_row(8, 30)
        self.worksheet.set_row(9, 30)
        self.worksheet.set_row(10, 30)

        # 设置两种格式,包含字体与背景
        define_format_H1 = self.get_format(self.workbook, {'bold': True, 'font_size': 18})
        define_format_H2 = self.get_format(self.workbook, {'bold': True, 'font_size': 14})
        define_format_H1.set_border(1)
        define_format_H2.set_border(1)
        define_format_H1.set_align("center")
        define_format_H2.set_align("center")
        define_format_H1.set_valign("vcenter")
        define_format_H2.set_valign("vcenter")
        define_format_H2.set_bg_color("gray")
        define_format_H2.set_color("#ffffff")

        # 初始化sheet1数据页
        self.worksheet.merge_range('A1:F1', '测试信息统计', define_format_H2)
        self.worksheet.merge_range('C2:F10', '图片预留位置', define_format_H1)
        self._write_center(self.worksheet, "A2", '测试开始时间')
        self._write_center(self.worksheet, "A3", '测试结束时间')
        self._write_center(self.worksheet, "A4", '测试总耗时(s)')
        self._write_center(self.worksheet, "A5", '测试项目名')
        self._write_center(self.worksheet, "A6", '测试接口数')
        self._write_center(self.worksheet, "A7", '运行用例数')
        self._write_center(self.worksheet, "A8", '通过用例数')
        self._write_center(self.worksheet, "A9", '失败用例数')
        self._write_center(self.worksheet, "A10", '测试通过率')

        self.worksheet.merge_range('A12:F12', '测试接口统计', define_format_H2)
        self._write_center(self.worksheet, "A13", '项目名称')
        self._write_center(self.worksheet, "B13", '接口名称')
        self._write_center(self.worksheet, "C13", '运行用例数')
        self._write_center(self.worksheet, "D13", '通过用例数')
        self._write_center(self.worksheet, "E13", '失败用例数')
        self._write_center(self.worksheet, "F13", '测试通过率')
       # self._write_center(self.worksheet, "G13", '失败用例id')
        self.logger.info('测试报告初始化数据完成....')

    def write_static_data(self, static_data, api_data):
        """
        写入统计数据
        :param static_data 测试概要统计数据
        :param api_data 测试接口统计数据
        """
        # 写入测试数据-统计数据
        if static_data is not None:
            self._write_center(self.worksheet, "B2", static_data['start_strftime'])
            self._write_center(self.worksheet, "B3", static_data['end_strftime'])
            self._write_center(self.worksheet, "B4", static_data['sum_time'])
            self._write_center(self.worksheet, "B5", static_data['proj_name'])
            self._write_center(self.worksheet, "B6", static_data['api_counts'])
            self._write_center(self.worksheet, "B7", static_data['cases_count'])
            self._write_center(self.worksheet, "B8", static_data['pass_counts'])
            self._write_center(self.worksheet, "B9", static_data['fail_counts'])
            self._write_center(self.worksheet, "B10", static_data['pass_rate'])

        # 写sheet1测试数据-api数据
        if api_data is not None:
            start_row = 14
            for proj in static_data['proj_name'].split(','):
                for k, v in api_data.items():
                    proj_name = api_data[k]['proj']
                    if proj_name in proj:
                        api_name = k
                        cases_counts = len(api_data[k]['pass'])+len(api_data[k]['fail'])
                        pass_counts = len(api_data[k]['pass'])
                        fail_counts = len(api_data[k]['fail'])
                        pass_rate = ("%.2f%%" % (pass_counts/cases_counts*100))
                        #fail_cases = ','.join(api_data[k]['fail'])
                        self._write_center(self.worksheet, "A"+str(start_row), proj_name)
                        self._write_center(self.worksheet, "B"+str(start_row), api_name)
                        self._write_center(self.worksheet, "C"+str(start_row), cases_counts)
                        self._write_center(self.worksheet, "D"+str(start_row), pass_counts)
                        self._write_center(self.worksheet, "E"+str(start_row), fail_counts)
                        self._write_center(self.worksheet, "F"+str(start_row), pass_rate)
                        #self._write_center(self.worksheet, "G"+str(start_row), fail_cases)
                        start_row += 1

            # 插入饼图
            self.pie()

    # 生成饼形图
    def pie(self):
        chart1 = self.workbook.add_chart({'type': 'pie'})
        chart1.add_series({
        'name':       '接口测试统计',
        'categories':'=测试总况!$A$8:$A$9',  # 饼图数据源，类目
        'values':    '=测试总况!$B$8:$B$9',  # 饼图数据源，数据
        'points': [
            {'fill': {'color': '#5ABA10'}},  # 红色
            {'fill': {'color': '#FE110E'}},  # 绿色
        ]
        })
        chart1.set_title({'name': '接口测试统计'})
        chart1.set_style(10)
        # 插入位置
        self.worksheet.insert_chart('C2', chart1, {'x_offset': 60, 'y_offset': 15})

if __name__ == "__main__":
    data_api = {
        'user': {
            'pass': ['mock-01', 'mock-02'],
            'fail': [],
            'proj': "用户中心"
        },
        'mockToken': {
            'pass': ['mock-03'],
            'fail': [],
            'proj': "mock管理中心"
        },
        'login': {
            'pass': ['mock-04', 'mock-05'],
            'fail': ['mock-06', 'mock-07'],
            'proj': "登录中心"
        },
        'testrele': {
            'pass': ['mock-08', 'mock-09'],
            'fail': [],
            'proj': "关联数据中心"
        }
    }
    data_static = {
        'title': '---------------------------运行结果概要统计:----------------------------',
        'start_strftime': '2018-05-31 15_17_09',
        'end_strftime': '2018-05-31 15_17_09',
        'sum_time': '0.07',
        'api_counts': 4,
        'cases_count': 9,
        'pass_counts': 7,
        'fail_counts': 2,
        'pass_rate': '77.78%',
        'fail_cases': ['mock-06', 'mock-07']
    }
    tr = Report()
    tr.init_data()
    tr.write_static_data(data_static, data_api)
    tr.close()
