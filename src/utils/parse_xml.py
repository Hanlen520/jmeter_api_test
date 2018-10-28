# -*- coding: utf-8 -*-
# @Time    : 2018/8/23 10:38
# @Author  : Burrows
# @FileName: parse_xml.py
'''工具类，用于解析jmeter结果文件（xml格式）'''

import json
import os, sys
import time
from xml.etree.ElementTree import parse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 将src路径加入环境变量

# from make_report import Report
from bases.read_logger import ReadLogger

class ParseXml:
    def __init__(self,filename):
        '''
        :param
            filename: 待统计的jtl文件名（jmeter测试结果文件）
        '''
        # 获取logger和run_log
        global logger
        global run_log_src
        read_logger = ReadLogger()
        logger = read_logger.get_logger()
        run_log_src = read_logger.get_run_log()
        self.filename = filename

        # 初始化excel报告
        # self.tr = Report()
        # self.tr.init_data()

        # 获取测试开始时间与时间戳
        global start_time
        global start_strftime
        root_dir=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 项目根路径
        time_file = root_dir + '/' + 'public_data' + '/' + 'time_file'
        with open(time_file, 'r') as fr:
          time_data = json.load(fr)
        start_time = time_data['start_time']
        start_strftime = time_data['start_strftime']

    # 获取excel文件
    # def get_file(self):
    #     return self.tr.get_file()

    # 获取概览数据，并写入excel文件
    def ParseXmlData(self):
        '''
        :return:
            dict_static_run, dict_static_api ：测试概要统计字典，接口概要统计字典
        '''
        f = open(self.filename, encoding='utf-8')
        et = parse(f)
        root = et.getroot()
        list_httpSample = list(root.iter('httpSample'))  # 拿到所有httpSample标签的描述符
        list_failure_sampler = []               # 失败的用例集:failure为true的sample
        list_rc_no_200_sampler = []             # 失败的用例集:rc不是200的sample
        list_pass_sampler = []                  # 通过的用例集
        list_tmp = []                           # 临时列表，存放所有用例名称,以便根据名称获取接口数
        list_run_pub = []                       # 公共用例列表
        dict_static_api = {}                       # api统计字典
        dict_static_run = {}                       # 运行概要统计字典

        count_list_pass_sampler = 0                  # 统计assert的failure为true的sample数
        count_list_fail_sampler = 0                  # 统计assert为failure为false的sample数
        count_list_rc_no_200_sampler = 0                 # 统计rc不是200的sample数

        # 用例使用 "项目名_接口名_用例id_用例描述" 的方式 命名测试sampler
        # 获取所有被测接口列表
        [list_tmp.append(f.get('lb')) for f in list_httpSample if f.get('lb').split('_')[0].strip() != "pub"]
        list_tmp2 = list(map(lambda x: x.split('_')[1].strip(), list_tmp))   # 临时列表，使用map方法拆分获取接口名
        list_all_api = list(set(list_tmp2))  # api总数

        # 初始化api统计字典
        for api in list_all_api:
            dict_static_api[api] = {'pass': [], 'fail': []}

        logger.info("开始统计测试结果数据....")

        # 迭代httpsample，如果需要判断用例通过，需要满足rc为200且断言通过2个条件
        for f in list_httpSample:
            # print("等待运行的用例总数：{_counts_case}".format(_counts_case=len(list_httpSample)))
            # 分离公共模块，如果是公共模块用例，则不加入统计结果。默认公共用例以 puModule_x_x_x 方式命名
            module = f.get('lb').split('_')[0].strip()  # 模块名
            api = f.get('lb').split('_')[1].strip()  # 接口名
            if module == "pub":
                # 公共用例
                list_run_pub.append(api)
            else:
                case_id = f.get('lb').split('_')[2].strip()  # 用例id
                # 首先判断响应码
                rc = f.get('rc')
                if rc != "200":
                    count_list_rc_no_200_sampler += 1
                    count_list_fail_sampler += 1
                    list_rc_no_200_sampler.append(case_id)
                    dict_static_api[api]['fail'].append(case_id)
                else:
                    # 然后判断failure值
                    failure = list(f.iter('failure'))  # 获取httpSample下的failure标签
                    for x in failure:
                        if x.text == "true":  # 断言不通过
                            # logger.info(x.text)
                            count_list_fail_sampler += 1
                            list_failure_sampler.append(case_id)
                            dict_static_api[api]['fail'].append(case_id)
                            break

                        if x.text == "false" and rc == "200":  # 断言通过
                            count_list_pass_sampler += 1
                            list_pass_sampler.append(case_id)
                            dict_static_api[api]['pass'].append(case_id)
                            break
                dict_static_api[api]['proj'] = module

        # 统计被测项目
        proj_list = []
        for k, v in dict_static_api.items():
            proj_list.append(v['proj'])

        # logger.info(dict_static_api)
        list_fail_sampler = list(set(list_failure_sampler + list_rc_no_200_sampler))         # 失败的用例集

        end_time = time.time()
        dict_static_run['title'] = "运行结果概要统计:".center(64, '-')
        dict_static_run['start_strftime'] = start_strftime  # 测试开始时间
        dict_static_run['end_strftime'] = time.strftime("%Y-%m-%d_%H-%M-%S")  # 测试结束时间
        dict_static_run['sum_time'] = "%.2f" % (end_time - start_time)  # 测试运行时间
        dict_static_run['proj_name'] = ','.join(set(proj_list))  # 测试包含项目
        dict_static_run['api_counts'] = len(list_all_api)  # 测试api总数
        dict_static_run['pubcases_count'] = len(list_run_pub)  # 公共用例数
        dict_static_run['cases_count'] = len(list_httpSample) - len(list_run_pub)  # 测试用例数，不包含公共用例
        dict_static_run['pass_counts'] = count_list_pass_sampler  # 通过测试用例总数
        dict_static_run['fail_counts'] = count_list_fail_sampler  # 未通过测试用例数
        dict_static_run['pass_rate'] = ("%.2f%%" % (dict_static_run['pass_counts']/dict_static_run['cases_count']*100))  # 测试通过率
        dict_static_run['fail_cases'] = ','.join(list_fail_sampler)  # 测试失败用例集

        str_static_run="""
                    {_title}
                    测试开始时间： {_start_strftime}
                    测试结束时间： {_end_strftime}
                    测试用时 (s)： {_sum_time}
                    测试项目名称： {_proj_name}
                    测试接口总数： {_api_counts}
                    公共的用例数： {_pubcase_count}
                    运行的用例数： {_cases_count}
                    通过的用例数： {_pass_counts}
                    失败的用例数： {_fail_counts}
                    测试通过率 ： {_pass_rate}
                    失败的用例集： {_fail_cases}
            """.format(
                _title=dict_static_run['title'],
                _start_strftime=dict_static_run['start_strftime'],
                _end_strftime=dict_static_run['end_strftime'],
                _sum_time=dict_static_run['sum_time'],
                _proj_name=dict_static_run['proj_name'],
                _api_counts=dict_static_run['api_counts'],
                _pubcase_count=dict_static_run['pubcases_count'],
                _cases_count=dict_static_run['cases_count'],
                _pass_counts=dict_static_run['pass_counts'],
                _fail_counts=dict_static_run['fail_counts'],
                _pass_rate=dict_static_run['pass_rate'],
                _fail_cases=dict_static_run['fail_cases']
                )
        logger.info(str_static_run)

        logger.info("运行接口详细统计:".center(64, '-'))
        # 子接口详细统计信息
        # {api_1:{'pass': [], 'fail': []},api_2:{'pass': [], 'fail': []}...}
        for k, v in dict_static_api.items():
            proj_name = v['proj']
            api_name = k
            run_cases = len(v['pass'])+len(v['fail'])
            pass_cases_counts = len(v['pass'])
            fail_cases_counts = len(v['fail'])
            pass_rate = ("%.2f%%" % (len(v['pass'])/(len(v['pass'])+len(v['fail']))*100))
            if len(v['fail']) == 0:
                fail_cases = None
            else:
                fail_cases = ",".join(v['fail'])
            logger.info("""
                    项目  名称： {_proj_name}
                    接口  名称： {_api_name}
                    运行用例数： {_run_cases}
                    通过用例数： {_pass_cases_counts}
                    失败用例数： {_fail_cases_counts}
                    测试通过率： {_pass_rate}
                    失败用例集： {_fail_cases}
            """.format(
                _proj_name=proj_name,
                _api_name=api_name,
                _run_cases=run_cases,
                _pass_cases_counts=pass_cases_counts,
                _fail_cases_counts=fail_cases_counts,
                _pass_rate=pass_rate,
                _fail_cases=fail_cases
                )
            )

            # self.tr.write_static_data(dict_static_run, dict_static_api)
            # self.tr.close()
        logger.info("测试结果数据统计完成....")
        print(dict_static_run)
        print(dict_static_api)
        return dict_static_run, dict_static_api
