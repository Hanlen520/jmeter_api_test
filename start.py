#! /usr/bin/python3
#####################################################################################
# 脚本名称：start.py
# 脚本描述：jmeter接口自动化执行入口
# 主要功能：执行ant构建jmx脚本文件，生成测试结果数据，并利用python整合测试结果数据，并生成最终报告，发送邮件给相关人员
# 作    者：lincoln_burrows
# 完成时间：2018-6-14
# 运行环境：python3、centos7
#####################################################################################
import json
import os
import sys
import time
import shutil
import configparser

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/' + 'src')

from utils.oper_sendmail import SendEmail
from utils.parse_xml import ParseXml
from bases.new_htmlfile import NewHtmlFile
from bases.read_logger import ReadLogger
from bases.oper_file import OperFile

class Start:
    def __init__(self, run_proj=None):
        self.op_file = OperFile()

        # 初始化变量
        global new_work_dir
        global run_proj_ins
        global op_sys
        op_sys = os.name.lower()
        run_proj_ins = run_proj
        self.d_time={}
        self.cases=[]
        pwd=os.path.dirname(os.path.abspath(__file__))  # 项目根路径
        if run_proj_ins is None :
            self.cases_dir=pwd + '/' + 'cases'
        else:
            self.cases_dir=pwd + '/' + 'cases' + '/' + run_proj_ins

        self.public_data_dir=pwd + '/' + 'public_data'
        self.workplace_dir=pwd + '/' + 'workplace'
        self.conf_dir=pwd + '/' + 'conf'
        if run_proj_ins is None:
            self.build_file=self.conf_dir + '/' + 'build.xml'
        else:
            self.build_file=self.conf_dir + '/' + 'build_' + run_proj_ins + '.xml'
        self.time_file = self.public_data_dir + '/' + 'time_file'
        # 依据当前时间，生成新文件夹 ant_report_new ，用于保存ant执行后数据.html和.jtl文件
        now=time.strftime("%Y-%m-%d_%H-%M-%S")
        self.new_dir='ant_report_{_now}'.format(_now=now)
        new_work_dir=self.workplace_dir + '/' + self.new_dir
        os.mkdir(new_work_dir)
        self.list_workplace = os.listdir(self.workplace_dir)
        self.list_new_dir = []
        self.ant_res_html=[]
        self.ant_res_jtl=[]

        # 获取logger和run_log
        read_logger = ReadLogger()
        self.logger = read_logger.get_logger()
        self.run_log_src = read_logger.get_run_log()
        self.run_log_dst = new_work_dir + '/' + 'run_' + now + '.log'

    # setup初始化环境
    def setup(self):
        # 初始化文件
        self.logger.info('开始初始化测试环境....')
        self.op_file.trunc_file(self.run_log_src)

        # 遍历cases下的.jmx文件，如果没有检测到测试用例，程序退出
        global cases_num
        for x in os.listdir(self.cases_dir):
            if x.endswith(".jmx"):
                self.cases.append(x.split('.jmx')[0])
        cases_num=len(self.cases)
        self.logger.info("待执行的测试用例数: {_cases_num}".format(_cases_num=cases_num))
        self.logger.info("待执行的测试用例名: {_cases}".format(_cases=', '.join(self.cases)))

        if len(self.cases) == 0:
            self.logger.info("没有检测到待执行用例，程序退出！")
            sys.exit(1)

        for x in os.listdir(self.workplace_dir):
            if x.endswith(".html"):
                os.remove(self.workplace_dir + '/' + x)
            if x.endswith(".jtl"):
                os.remove(self.workplace_dir + '/' + x)

        # 记录测试开始时间和时间戳
        self.d_time['start_time'] = time.time()
        self.d_time['start_strftime'] = time.strftime("%Y-%m-%d %H_%M_%S")
        new_time = json.dumps(self.d_time,ensure_ascii=False, indent=2, sort_keys=True)
        with open (self.time_file,'w') as fw:
            fw.write(new_time)
        self.logger.info("测试开始时间:{_start_time}".format(_start_time=self.d_time['start_strftime']))

        #with open (time_file,'r') as fr:
        #  time_data = json.load(fr)

        # 获取当前最新的workplace工作路径
        for x in self.list_workplace:
            if x.startswith("ant_report_"):
                self.list_new_dir.append(x)
        self.list_new_dir.sort(key=lambda fn: os.path.getmtime(self.workplace_dir + '/' + fn))
        new_ant_report_dir = self.list_new_dir[-1]
        self.logger.info("生成最新的工作文件夹: {_dirname}".format(_dirname=new_ant_report_dir))
        self.logger.info('初始化测试环境完成....')

    # 恢复环境
    def tear_down(self):
        self.logger.info('测试运行完成，开始恢复环境....')
        self.logger.info('恢复环境完成，程序退出....')
        self.op_file.copy_file(self.run_log_src, self.run_log_dst)

    # 执行ant构建
    def ant_build(self):
        # 遍历cases下的.jmx文件，使用ant依次执行，生成的.html与.jtl文件保存到workplace下的ant_report_new
        for case in self.cases:
            self.logger.info("开始构建脚本:{_case}".format(_case=case).center(64,'-'))
            if op_sys == "posix":
                self.logger.info(os.system('ant -file {_build_file} -Dtest={_case} | tee -a {_log_file}'.format(_build_file=self.build_file, _case=case, _log_file=self.run_log_src)))
            elif op_sys == "nt":
                print(os.system('ant -file {_build_file} -Dtest={_case}'.format(_build_file=self.build_file, _case=case)))
            else:
                self.logger.info("不支持的操作系统，程序退出...")
                sys.exit(-3)
            self.logger.info("构建脚本{_case}完成".format(_case=case).center(64,'-'))
        # 数据结果文件检查
        for x in os.listdir(self.workplace_dir):
            if x.endswith(".html"):
                self.ant_res_html.append(x)
            if x.endswith(".jtl"):
                self.ant_res_jtl.append(x)
        # self.logger.info(self.ant_res_html)
        # self.logger.info(self.ant_res_jtl)
        if len(self.ant_res_html) != cases_num or len(self.ant_res_jtl) != cases_num:
            self.logger.info("ant构建结果失败！请检查测试用例配置或ant配置")
            sys.exit(1)
        else:
            for f in self.ant_res_html:
                shutil.move(self.workplace_dir + '/' + f, new_work_dir + '/')
            for f in self.ant_res_jtl:
                shutil.move(self.workplace_dir + '/' + f, new_work_dir + '/')

    # 重构测试数据与报告
    def reviw_testdata(self):
        # 遍历ant_report_new下的.html和.jtl文件,操作并生成新的.html和.jtl的临时文件.tmp,组合为新的 report.html与report.jtl文件
        self.logger.info("开始重构测试数据....")
        tmp_html_list=[]
        tmp_jtl_list=[]
        for x in os.listdir(new_work_dir):
            x=new_work_dir + '/' + x
            if x.endswith(".html"):
                with open(x, 'r', encoding="utf-8") as f:
                    html_content = f.readlines()  # 一次性读取所有内容，并按行返回list
                    for index, cot in enumerate(html_content):
                        if index <= 100:
                            html_content.pop(0)
                    html_content[0] = html_content[0].replace("</script></head><body><div id=\"left-panel\"><ol id=\"result-list\"><li class=\"navigation\">Thread: JIATUI_API_TEST 1-1</li>", "")
                    html_content[-1] = html_content[-1].replace("</ol></div><div id=\"right-panel\"></div></body></html>", "")
                tmp_html_list = tmp_html_list + html_content
            if x.endswith(".jtl"):
                with open(x, 'r', encoding="utf-8") as f:
                    jtl_content = f.readlines()
                    jtl_content.pop(-1)
                    jtl_content.pop(-1)
                    jtl_content.pop(0)
                    jtl_content.pop(0)
                tmp_jtl_list = tmp_jtl_list + jtl_content

        new_report_html = new_work_dir + '/' + 'test_report.html'  # 重组后的html报告
        new_report_jtl = new_work_dir + '/' + 'test_report.jtl'  # 重组后的jtl数据
        report_html_header_data = self.public_data_dir + '/' + 'report_html_header.data'
        report_html_ender_data = self.public_data_dir + '/' + 'report_html_ender.data'
        report_jtl_header_data = self.public_data_dir + '/' + 'report_jtl_header.data'
        report_jtl_ender_data = self.public_data_dir + '/' + 'report_jtl_ender.data'

        # 重组html报告
        with open(report_html_header_data, 'r', encoding="utf-8") as f_head:
            head = f_head.readlines()

        with open(report_html_ender_data, 'r', encoding="utf-8") as f_end:
            end = f_end.readlines()

        html = head + tmp_html_list + end

        with open(new_report_html, 'w', encoding="utf-8") as f:
            f.writelines(html)

        # 重组jtl报告
        with open(report_jtl_header_data, 'r', encoding="utf-8") as f_head:
            head = f_head.readlines()

        with open(report_jtl_ender_data, 'r', encoding="utf-8") as f_end:
            end = f_end.readlines()

        jtl = head + tmp_jtl_list + end

        with open(new_report_jtl, 'w', encoding="utf-8") as f:
            f.writelines(jtl)

        self.logger.info("重构测试数据完成....")

    # 分析test_report.jtl文件，获取运行概览统计字典与运行详细统计字典
    def reviw_report(self):
        global dict_static_run, dict_static_api
        newHtmlFile = NewHtmlFile()
        htmlFile, htmlFilePath, jtlFile, jtlPath = newHtmlFile.get_newfile()
        test_xml_file = jtlPath
        px = ParseXml(test_xml_file)
        dict_static_run, dict_static_api = px.ParseXmlData()

    # 发送邮件，附件内容为测试概览报告和测试详细报告
    def sendmail(self):
        cf = configparser.ConfigParser()
        conf_file = self.conf_dir + '/' + 'conf.ini'
        cf.read(conf_file)
        smtp_server = cf.get('email-conf', 'smtp_server')           # smtp服务器
        send_user = cf.get('email-conf', 'sender')       # 登录邮箱
        password = cf.get('email-conf', 'password')                # 登录密码，如果是第三方邮箱如163，需要用授权码登录
        if run_proj_ins is None:
            receiver_list = cf.get('email-conf', 'receiver')
        elif run_proj_ins in 'events':
            receiver_list = cf.get('email-conf', 'receiver_events')
        elif run_proj_ins in 'users':
            receiver_list = cf.get('email-conf', 'receiver_users')
        elif run_proj_ins in 'shop':
            receiver_list = cf.get('email-conf', 'receiver_shop')
        else:
            receiver_list = cf.get('email-conf', 'receiver')
        # sen = SendEmail(recv)

        sen = SendEmail(smtp_server, send_user, password, receiver_list)
        sen.send_main(dict_static_run, dict_static_api)

if __name__ == '__main__':
    args_list = sys.argv
    run_proj = None
    if len(args_list) == 1:
        pass
    elif len(args_list) > 2:
        print('args num error!')
        sys.exit(1)
    elif args_list[1] in 'events':
        print('test events...')
        run_proj = "events"
    elif args_list[1] in 'users':
        print('test users...')
        run_proj = "users"
    elif args_list[1] in 'shop':
        print('test shop...')
        run_proj = "shop"
    else:
        print('args error!')
        sys.exit(1)

    start = Start(run_proj)
    start.setup()
    start.ant_build()
    start.reviw_testdata()
    start.reviw_report()
    start.tear_down()
    #start.sendmail()
