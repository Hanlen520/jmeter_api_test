* # 框架简介
    - jmeter_api_test ，基于jmeter+ant+python封装的接口自动化测试框架

* # 注意事项
    - 暂时只在linux环境下调试运行成功

* # 框架特色
    - 灵活配置：支持以配置文件的方式管理配置，如日志配置与email配置等
    - 报告记录：测试结果报告记录丰富，包含 测试概览报告 与 测试详细报告 等，简单易读
    - 多人协作：支持多人.jmx用例同时构建，不影响测试报告输出
    - 邮件支持：支持基于smtp的方式发送email
    - 兼容性强：基于jmeter进行测试和用例开发，充分利用jmeter兼容和扩展性强的特点，协议和插件支持丰富
    - 扩展性强：基于python3开发，方便后续对框架功能的扩展

* # 目录结构
    - /cases        ： 用例目录，用于管理jmeter的.jmx测试用例文件
    - /src          ： python源码目录
    - /conf         ： 配置文件目录，包含构建配置、邮件配置、日志配置等
    - /log          ： 运行时日志目录
    - /public_data  ： 公共数据目录
    - /workplace    ： ant构建的工作目录，根据测试执行时间生成每次生成新子目录ant_report_${now}
    - start.py      ： 框架执行入口

* # 运行环境
    - centos7+,windows
    - jdk1.8+
    - jmeter3.1+,jmeter4.0
    - ant1.9.7+
    - python3.6+

* # 运行依赖
    - 配置jmeter+ant构建环境，确保jmeter可以执行构建成功

* # 用例要求
    - 线程组
        - 名称：JIATUI_API_TEST （固定写法，不要有空格）
        - 数量：1（当前版本在多个线程组运行时，测试统计结果数据出错）
    - 用例
        - 名称：{项目名称}_{接口名称}_{用例ID}_{用例描述}（用下划线_分隔，用例ID建议用【项目名首字母大写-接口名称英文驼峰写法{ID号}】）
     - 路径管理
        - 路径兼容：参数化文件、include控制器等脚本中涉及文件路径引入的，建议使用相对路径的方式引入，这样保持linux或windows下路径结构一致，可解决路径的兼容性问题,例如脚本在/data/jiatui/cases/test.jmx,数据在/data/jiatui/csv_data/test.data则在test.jmx引入路径的方式为 ../csv_data/test.data
        - 引包兼容：涉及第三方jar包的引入，建议放到${jmeter_home}/lib/ext/下，无需在脚本中再次引入

