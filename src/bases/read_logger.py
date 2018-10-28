# -*- coding: utf-8 -*-
# @Time    : 2018/6/16 9:53
# @Author  : Burrows
# @FileName: read_logger.py
"""基础类，用于读取日志配置和和获取日志文件"""
import os
import logging
import logging.config


class ReadLogger:
    def __init__(self):
        # 读取日志配置
        root_dir=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 项目根路径
        log_conf_file = 'logging.conf'  # 日志配置文件
        log_path = root_dir + '/' + 'conf' + '/' + log_conf_file  # 日志配置文件绝对路径
        logging.config.fileConfig(log_path)
        self.logger = logging.getLogger('simpleExample')
        # 生成日志文件
        log_src = "run.log"  # 运行时日志
        self.run_log_src = root_dir + '/' + 'log' + '/' + log_src

    # 获取logger容器
    def get_logger(self):
        return self.logger

    # 获取日志文件路径
    def get_run_log(self):
        return self.run_log_src

if __name__ == "__main__":
    rl = ReadLogger()
    logger = rl.get_logger()
    logger.debug('debug message')
    s = 'hehehehheeh'
    logger.info('%s' % s)
    logger.info(u'中文信息')
    logger.warn('----{warn_msg1}----,----{warn_msg2}----'.format(warn_msg1="test-warn_msg1", warn_msg2="test-warn_msg2"))
    logger.error('error message')
    logger.critical('critical message')
