![WonderTrader2.png](http://wt.f-sailors.cn/wt/logo_qcode_noad.jpg)
<p align="center">
    <img src ="https://img.shields.io/badge/version-0.8.0-blueviolet.svg"/>
    <img src ="https://img.shields.io/badge/platform-windows|linux-yellow.svg"/>
    <img src ="https://img.shields.io/badge/build-passing-brightgreen"/>
    <img src ="https://img.shields.io/badge/license-MIT-orange"/>
</p>

# wtpy
这是**WonderTrader**针对`Python3`适配的子框架

# wtpy子框架简介
+ apps子模块
    > - WtBtAnalyst.py	回测分析模块，主要是利用回测生成的数据，计算各项回测指标，并输出到`excel`文件
    > - WtCtaOptimizer  `CTA`优化器，主要是利用`multiprocessing`并行回测，并统计各项交易指标，最后将统计结果汇总输出到`csv`文件
	> - WtHotPicker		国内期货换月规则辅助模块，支持从交易所网站页面爬取数据确定换月规则，也支持解析`datakit`每日收盘生成的snapshot.csv来确定换月规则
+ wrapper子模块
	> 该模块主要包含了所有和`C++`底层对接的接口模块
	> - ContractLoader.py	主要用于通过`CTP`等接口加载基础的`commodities.json`和`contracts.json`文件
	> - WtBtWrapper.py	主要用于和回测引擎`C++`核心模块对接
	> - WtDtWrapper.py	主要用于和数据组件`C++`核心模块对接
	> - WtDtHelper.py	主要提供将用户自己的数据和`WonderTrader`内部数据格式进行转换的功能
	> - WtDtServoApi.py	主要向用户提供直接通过`python`访问`datakit`落地的数据的接口	
	> - WtExecApi.py	主要用于和`C++`独立执行模块`WtExecMon`对接
	> - WtWrapper.py	主要用于和实盘交易引擎`C++`核心模块对接
	> - WtMQWrapper.py	主要提供直接使用底层WtMsgQue模块的对接
    > - WtDtHelper.py   主要用于和底层的`WtDtHelper`数据辅助模块对接
+ monitor子模块
	> 该模块主要包含了内置的监控服务，提供了`Http`和`websocket`两种连接方式
	> - DataMgr.py	主要用于读取并缓存组合数据
	> - EventReceiver.py	主要用于在指定的`udp`端口接收组合转发的各种事件
	> - PushSvr.py	主要用于向`web`提供`websocket`服务
	> - WatchDog.py	主要用于自动调度服务端的进程
	> - WtBtMon.py	主要进行回测的管理
	> - WtMonSvr.py	监控服务核心服务模块 ，利用`flask`实现了一个`http`服务接口
	> - static		`webui`静态文件
+ 其他模块
	> 主要位于根节点下，包含了各个子模块的入口组件
	> - WtCoreDefs.py	主要定义的`Python`版本的策略基类，方便用户重写
	> - CodeHelper.py 品种代码辅助模块，内置了一些方法，方便使用
	> - ContractMgr.py 合约管理器模块，用于加载`contracts.json`或`stocks.json`文件，并提供查询方法
	> - CtaContext.py	主要定义了`CTA`策略的上下文，可以理解为单策略的运行环境
	> - HftContext.py	主要定义了`HFT`策略的上下文，可以理解为单策略的运行环境
	> - SelContext.py	主要定义了`SEL`策略的上下文，可以理解为单策略的运行环境
	> - ExtToolDefs.py	扩展模块定义文件，主要定义了一些扩展模块的基础接口
	> - ProductMgr.py	品种管理器，主要用于`Python`环境中的合约属性、品种属性查询
	> - SelContext.py	选股策略上下文，即选股策略直接交互的`API`
	> - SessionMgr.py	交易时间模板管理器，主要用于`Python`环境中的交易时段模板管理
	> - StrategyDefs.py	各引擎策略基础定义模块，定义了`CTA`、`HFT`、`SEL`三种策略基类
	> - WtBtEngine.py	回测引擎转换模块，主要封装底层接口调用
	> - WtDtEngine.py	数据引擎转换模块，主要封装底层接口调用
	> -	WtEngine.py		交易引擎转换模块，主要封装底层接口调用



# 更新日志
### 0.8.0(大版本)
* `C++`底层更新到`2021/12/24`发布的`v0.8.0`版本
* （**重要**）实现了ExtDataLoder的机制，实盘和回测框架都可以通过应用层的扩展数据加载器加载历史数据（可参考demos/test_dataexts）
* （**重要**）实现了ExtDataDumper的机制，如果向datakit注册了ExtDataDumper，在收盘作业的时候，就会通过ExtDataDumper将实时数据转储（可参考demos/test_dataexts）
* （**重要**）配合C++完善了对T+1交易机制的支持
* WatchDog模块做了调整，增加了对进程使用的内存的监控
* 新增了一个高性能容器DequeRecord（By **ZerounNet**），用于python部分的缓存替换原来的WtKlinData和WtHftData，在数据缓存方面，大致可以提升5%~10%的性能
* demos下新增一个cta_unit_test，作为一个基准测试demo，以后会逐步完善
* 其他细节优化和bug修正

### 0.7.1
* `C++`底层更新到`2021/10/24`发布的`v0.7.1`版本
* 回测框架`C++`底层增加了单步控制机制，用于控制回测进度，主要为了配合强化学习框架的调用习惯
* `WtDtEngine`支持扩展`Parser`的接入，可以参考`/demos/datakit_fut/testExtParser.py`
* 其他配合底层的优化和调整

### 0.7.0
* `C++`底层更新到`2021/09/12`发布的`v0.7.0`版本
* 新增一个`WtDataServo`模块，分为两种实现方式， 一种是调用本地底层`WtDtServo`模块，直接访问数据文件，根据需要可开启`web`接口，另外一种是直接访问第一种实现方式提供的`web`接口拉取数据，详情可以参考`/demos/test_dataservo`
* 优化了`WtWrapper`和`WtBtWrapper`，将原来的`global`变量全部改成局部变量，可以提升运行效率
* 通过`singleton`修饰器限定`Wrapper`为单例，和底层统一
* 新增一个`WtMsgQue`模块，通过`WtMQWrapper`模块调用底层的`WtMsgQue`模块
* `EventReceiver`模块改成调用`WtMsgQue`来实现，并按照回测和实盘框架分别实现`EventReceiver`
* `WatchDog`启动和监控进程的机制进行了优化，不再使用`threading`挂载进程句柄的方式，而是利用`cmdline`和`processid`进行检查和监控，这样`WtMonSvr`重启之后，就可以重新根据命令行挂在已经在运行的进程
* `WtMonSvr`新增回测管理模块`WtBtMon`，用于提供回测相关的接口服务
* `WtMonSvr`完善了组合配置文件查询和修改的接口
* `WtMonSvr`完善了组合风控过滤器`filters.json`的读取机制
* `WtMonSvr`新增了用户修改密码和管理员重设用户密码的接口
* `PushSvr`根据`EventReceiver`收到的数据，进行了适配，完善了消息推送的机制
* `WtBtAnalyst`模块新增了`run_simple`接口，用于只进行最简单的每日资金分析，并将结果输出到`summary.json`文件
* `apps`下新增了一个`WtHotPicker.py`模块，用于确定主力合约和次主力合约
* 其他配合底层的优化和调整
* `webui`剥离出来，单独发布到`wtconsole`仓库

### 0.6.5
* `C++`底层更新到`2021/07/19`发布的`v0.6.5`版本
* `WtDtHelper`新增一个`resample_bars`接口，用于将制定的`dsb`数据文件重新采样为其他周期的K线
* `SessionInfo`新增一个`toString`对象，生成`json`格式的字符串
* 暴力优化器`CTAOptimizer`支持设置多个回测时段
* 完善了`read_dsb_bars`和`read_dsb_ticks`接口，同时新增`read_dmb_bars`和`read_dmb_ticks`接口调用`WtDtHelper.dll`的同名接口
* `Context`新增一个`is_backtest`属性，用于判断是否在回测模式
* 监控服务新增了查看组合文件结构、获取组合下文件内容以及修改组合下文件内容的接口
* 完善了`webui`控制台针对风控员的权限控制
* 完善了绩效分析模块的兼容性
* `webui`完善
* 其他代码级的优化和完善

### 0.6.4
* `C++`底层更新到`2021/05/24`发布的`v0.6.4`版本
* `WtDtHelper`中调用优化，去掉了`global`
* 修正了一些底层接口调用时参数对应不上的问题
* `WtDtHelper`新增了直接从`python`里向`C++`底层喂历史数据的接口`trans_bars`和`trans_ticks`
* 新增了一些`demo`
* 针对`C++`底层进行适配：1、`CTA`增加一个`stra_get_fund_data`接口，2、回测引擎，支持设置`slippage`
* `WtEngine`构造函数提供指定数据输出目录的`genDir`参数，以及日志配置文件的`logCfg`参数
* 其他代码级的优化和完善

### 0.6.3
* `C++`底层更新到`2021/04/14`发布的`v0.6.3`版本
* 绩效分析工具`WtBtAnalyst`功能大幅度扩展

### 0.6.2
* `C++`底层更新到`2021/03/17`发布的`v0.6.2`版本
* 日志信息翻译成英文
* `webui`的部分表格添加了排序和统计功能

### 0.6.1
* `C++`底层更新到`2021/02/26`发布的`v0.6.1`版本
* 统一封装了一个`PlatformHelper`模块，用于确定操作系统的各种信息
* 将绝大部分的函数参数和返回值都增加了类型，方便调用的时候查看
* 将K线容器类的成员变量做了修改，`size`->`capacity`，`count`->`size`，便于用户理解
* `WtDtHelper`模块新增两个接口`read_dsb_ticks`和`read_dsb_bars`，同步调用`C++`底层`WtDtHelper`模块的同名接口，用于直接读取`dsb`文件
* `CTA`策略新增一个`stra_get_last_exittime`用于获取上一个出场信号
* `WtBeEngine`和`WtCtaOptimizer`两个模块都增加了对`C++`策略的支持
* 回测框架增加对`session`开始和结束事件的响应接口
* 监控服务：增加了查看和修改入口脚本的接口`/qrygrpentry`、`/cmtgrpentry`
* `web-ui`：去掉`vue-json-viewer`库，改用`codemirror`，用于展示和编辑代码
* `web-ui`：控制台新增入口代码修改的组件，用于修改组合盘下的`run.py`入口文件
* `web-ui`：优化了一些展示的细节
* `wtpy.apps`下添加了一个`datahelper`子模块，该模块的主要作用就是将不同数据源的数据按照`WonderTrader`支持的格式保存起来

### 0.6.0
* `C++`底层更新到`2021/01/26`发布的`v0.6.0`版本
* `CTA`策略`API`新增一个`stra_get_tdate`，用于获取当前交易日
* `CTA`策略`API`和`SEL`策略`API`各新增一个`stra_get_all_position`，用于获取全部的持仓数据
* 完善了`WtBtWrappe`r模块中对`tick`数据的处理
* 完善了数据辅助模块`WtDtHelper`
* 完善了跟`C++`底层新增的HFT接口的对接
* 初步完成了跟`C++`底层新增的股票`Level2`数据访问接口的对接
* 将`WtDataDefs`模块中的`WtTickData`改成`WtHftData`，作为高频数据的通用容器

### 0.5.4.1
* `WatchDog`模块中修改了一周星期的序列，因为`Python`从周一到周天标记为0-6，而`WonderTrader`采用周天到周六为0-6

### 0.5.4
* `C++`底层更新到`2020/12/25`发布的`v0.5.4`版本
* `C++`底层接口针对传递配置文件内容的支持做了修改，同步修改了`wtpy`中的部分关联代码
* 修正了监控服务中的`WatchDog`模块在`linux`下的启动参数的`bug`，解决了`linux`下无法启动的问题
* 修正了监控服务的自动调度任务没有检查是否启用标记，从而导致重复启动的`bug`
* 修改了监控服务的`WebUI`的一些展示细节
* `wrapper`下新增一个`WtDtHelper`模块，用于对接`C++`底层的`WtDtHelpe`r模块，给`python`调用处理数据转换的任务
* 将`WtBtAnalyst`模块迁移到`wtpy.apps`下
* 新增一个`WtOptimizer`，用于遍历优化策略参数

### 0.5.3
* `CTPLoader`增加一个isMini的参数，用于控制底层调用MiniLoader对接CTPMini2进行拉取
* `WtKlineData`新增一个slice方法，用于对已有K线进行切片
* `C++`底层更新到2020/12/08发布的`v0.5.3`版本
* `CtaContext`新增一个`stra_get_sessinfo`接口，用于获取品种的交易时间信息
* `monitor`模块中的`web-gui`修改了一些bug
* 修正了绩效分析模块的一些bug

### 0.5.2
* 同步`WonderTrader`核心为v0.5.2
* 监控服务`monitor`增加了一个日志模块`WtLogger.py`，内部使用`logging`模块来记录日志
* 进一步完善了`web-ui`的部分功能和配色
* 新增一个`CTPLoader`模块，主要用于调用底层`CTPLoader`执行程序，用于从`CTP`账号加载合约列表

### 0.5.1
* 同步`WonderTrader`核心为v0.5.1
* 新增一个`monitor`监控服务模块，其中包含`http`服务、`websocket`服务两种对web端提供的服务，同时新增了组合事件组件，用于接收组合转发出来的实时事件，还新增一个调度模块用于自动调度服务器上的定时任务
* 新增一个`web-ui`目录，用于管理`wtpy`的`web-ui`项目，暂时实现了PC版的监控界面，位于`web-ui/console`下，`web-ui`采用`vue2+webpack`来实现，前端采用`element-ui`界面库，能够实时提供强大的组合盘监控服务

### 0.5.0
* 同步`WonderTrader`核心为v0.5.0
* 引入了`hft`策略以后，策略可以直接调用行情接入模块`Parsers`，所以调整C++底层模块的目录结构，方便策略调用
* 增加了`HftContext`以及`BaseHftStrategy`两个针对HFT策略的基础模块
* 回测和实盘都完成了跟C++底层的HFT接口的对接

### 0.4.0
* 新增一个**SEL引擎**，用于调度应用层的选股策略，得到目标组合以后，提供自动执行服务，暂时只支持日级别以上的调度周期，执行会放到第二天
* 因为新增了选股调度引擎，所以全面重构`WtPorter`和`WtBtPorter`导出的接口函数，以便调用的时候区分
* 新增一个**独立的执行器模块**`WtExecMon`，并导出C接口提供服务。主要是剥离了策略引擎逻辑，提供单纯的执行服务，方便作为单纯的执行通道，嫁接到其他框架之下
* `Windows`下的开发环境从`vs2013`升级到`vs2017`，`boost1.72`和`curl`需要同步升级

### 0.3.6
* 执行器使用线程池，减少对网络线程的时间占用
* 增加了一个实盘仿真模块`TraderMocker`，可以满足目前已经支持的股票和期货的仿真交易
* 更多接口支持（飞马、易盛iTap、`CTPMini`）
* 内置执行算法增加`TWAP`
* 继续完善文档

### 0.3.5
* 把手数相关的都从整数改成浮点数，主要目的是为了以后兼容虚拟币交易(虚拟币交易数量都是小数单位)
* 优化手数改成浮点数以后带来的日志输出不简洁的问题(浮点数打印会显示很多“0000”)
* 逐步完善文档
* XTP实盘适配，主要是修复`bug`

### 0.3.4
* 正式开源的第一个版本