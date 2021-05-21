代码重要
* 获得主力合约的下一个合约
* 获取收盘时间有bug
* 强烈需要 before_market_start after_market_end之类的on event方法
* ~~暴露设置滑点的方法~~
* ~~on_calculate里通过Context获得“当前权益”~~
* ~~生产和回测的数据存放目录结构统一文件名统一，csv生成dsb的时候按照目录结构和文件名~~
* 整个目录csv的转化成结构话dsb目前没有太好办法，只能通过模拟一个回测
* datakit的配置文件中code有问题，顺便支持 code:"CFFEX.T.HOT"或 code:"CFFEX.T" 类似的配置
* "module":"WtRiskMonFact.dll" 类似配置改为 "module":"WtRiskMonFact"，自动判断dll或so以便兼容linux和win
* ~~CSV转BIN需要支持hold字段~~

代码次要
* 跟合约相关的filename、stdcode规则统一  CFFEX.T2109和CFFEX.T.2109
* 跟交易通道、行情通道的用户密码相关的配置最好独立一个文件
* statemonitor.json、logcfg.json、logcfgbt.json存放位置硬编码
* datakit落地时可以配置是否落地tick m1
* 分析器'Strategy[%s]_PnLAnalyzing_%s_%s.xlsx'文件可指定目录
* ctpdata、generated两个目录位置可配置，ctploader似乎也有ctpdata的的东西。
* Common/holidays.json Common/sessions.json 两个文件的自动生成

文档重要
* 下单模式（市价、对手价、中间价）的配置文档
* filter的配置
* riskmon及相关module的配置
* actpolicy的配置

建议
* ~~收盘作业能否维护主力合约映射更新，已经通过其他方式实现~~