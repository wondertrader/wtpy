# wtpy
这是**WonderTrader**针对`Python3`适配的子框架

# wtpy子框架简介
+ apps子模块
    > - WtBtAnalyst.py	回测分析模块，主要是利用回测生成的数据，计算各项回测指标，并输出到excel文件
    > - WtCtaOptimizer  `CTA`优化器，主要是利用`multiprocessing`并行回测，并统计各项交易指标，最后将统计结果汇总输出到`csv`文件
+ wrapper子模块
	> 该模块主要包含了所有和`C++`底层对接的接口模块
	> - WtBtWrapper.py	主要用于和回测引擎`C++`核心模块对接
	> - WtDtWrapper.py	主要用于和数据组件`C++`核心模块对接
	> - WtExecApi.py	主要用于和`C++`独立执行模块`WtExecMon`对接
	> - WtWrapper.py	主要用于和实盘交易引擎`C++`核心模块对接
    > - WtDtHelper.py   主要用于和底层的`WtDtHelper`数据辅助模块对接
+ monitor子模块
	> 该模块主要包含了内置的监控服务，提供了`Http`和`websocket`两种连接方式
	> - DataMgr.py	主要用于读取并缓存组合数据
	> - EventReceiver.py	主要用于在指定的`udp`端口接收组合转发的各种事件
	> - PushSvr.py	主要用于向`web`提供`websocket`服务
	> - WatchDog.py	主要用于自动调度服务端的进程
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
### 0.3.4
* 正式开源的第一个版本


### 0.3.5
* 把手数相关的都从整数改成浮点数，主要目的是为了以后兼容虚拟币交易(虚拟币交易数量都是小数单位)
* 优化手数改成浮点数以后带来的日志输出不简洁的问题(浮点数打印会显示很多“0000”)
* 逐步完善文档
* XTP实盘适配，主要是修复`bug`

### 0.3.6
* 执行器使用线程池，减少对网络线程的时间占用
* 增加了一个实盘仿真模块`TraderMocker`，可以满足目前已经支持的股票和期货的仿真交易
* 更多接口支持（飞马、易盛iTap、`CTPMini`）
* 内置执行算法增加`TWAP`
* 继续完善文档

### 0.4.0
* 新增一个**选股调度引擎**，用于调度应用层的选股策略，得到目标组合以后，提供自动执行服务，暂时只支持日级别以上的调度周期，执行会放到第二天
* 因为新增了选股调度引擎，所以全面重构`WtPorter`和`WtBtPorter`导出的接口函数，以便调用的时候区分
* 新增一个**独立的执行器模块**`WtExecMon`，并导出C接口提供服务。主要是剥离了策略引擎逻辑，提供单纯的执行服务，方便作为单纯的执行通道，嫁接到其他框架之下
* `Windows`下的开发环境从`vs2013`升级到`vs2017`，`boost1.72`和`curl`需要同步升级

### 0.5.0
* 同步`WonderTrader`核心为v0.5.0
* 引入了`hft`策略以后，策略可以直接调用行情接入模块`Parsers`，所以调整C++底层模块的目录结构，方便策略调用
* 增加了`HftContext`以及`BaseHftStrategy`两个针对HFT策略的基础模块
* 回测和实盘都完成了跟C++底层的HFT接口的对接

### 0.5.1
* 同步`WonderTrader`核心为v0.5.1
* 新增一个`monitor`监控服务模块，其中包含`http`服务、`websocket`服务两种对web端提供的服务，同时新增了组合事件组件，用于接收组合转发出来的实时事件，还新增一个调度模块用于自动调度服务器上的定时任务
* 新增一个`web-ui`目录，用于管理`wtpy`的`web-ui`项目，暂时实现了PC版的监控界面，位于`web-ui/console`下，`web-ui`采用`vue2+webpack`来实现，前端采用`element-ui`界面库，能够实时提供强大的组合盘监控服务

### 0.5.2
* 同步`WonderTrader`核心为v0.5.2
* 监控服务`monitor`增加了一个日志模块`WtLogger.py`，内部使用`logging`模块来记录日志
* 进一步完善了`web-ui`的部分功能和配色
* 新增一个`CTPLoader`模块，主要用于调用底层`CTPLoader`执行程序，用于从`CTP`账号加载合约列表

### 0.5.3
* `CTPLoader`增加一个isMini的参数，用于控制底层调用MiniLoader对接CTPMini2进行拉取
* `WtKlineData`新增一个slice方法，用于对已有K线进行切片
* `C++`底层更新到2020/12/08发布的`v0.5.3`版本
* `CtaContext`新增一个`stra_get_sessinfo`接口，用于获取品种的交易时间信息
* `monitor`模块中的`web-gui`修改了一些bug
* 修正了绩效分析模块的一些bug

### 0.5.4
* C++底层更新到2020/12/25发布的v0.5.4版本
* `C++`底层接口针对传递配置文件内容的支持做了修改，同步修改了`wtpy`中的部分关联代码
* 修正了监控服务中的`WatchDog`模块在`linux`下的启动参数的`bug`，解决了`linux`下无法启动的问题
* 修正了监控服务的自动调度任务没有检查是否启用标记，从而导致重复启动的`bug`
* 修改了监控服务的`WebUI`的一些展示细节
* `wrapper`下新增一个`WtDtHelper`模块，用于对接`C++`底层的`WtDtHelpe`r模块，给`python`调用处理数据转换的任务
* 将`WtBtAnalyst`模块迁移到`wtpy.apps`下
* 新增一个`WtOptimizer`，用于遍历优化策略参数

### 0.5.4.1
* WatchDog模块中修改了一周星期的序列，因为Python从周一到周天标记为0-6，而WonderTrader采用周天到周六为0-6

### 0.6.0
* C++底层更新到2021/01/26发布的v0.6.0版本
* CTA策略API新增一个stra_get_tdate，用于获取当前交易日
* CTA策略API和SEL策略API各新增一个stra_get_all_position，用于获取全部的持仓数据
* 完善了WtBtWrapper模块中对tick数据的处理
* 完善了数据辅助模块WtDtHelper
* 完善了跟C++底层新增的HFT接口的对接
* 初步完成了跟C++底层新增的股票Level2数据访问接口的对接
* 将WtDataDefs模块中的WtTickData改成WtHftData，作为高频数据的通用容器

### 0.6.1
* C++底层更新到2021/02/26发布的v0.6.1版本
* 统一封装了一个PlatformHelper模块，用于确定操作系统的各种信息
* 将绝大部分的函数参数和返回值都增加了类型，方便调用的时候查看
* 将K线容器类的成员变量做了修改，size->capacity，count->size，便于用户理解
* WtDtHelper模块新增两个接口read_dsb_ticks和read_dsb_bars，同步调用C++底层WtDtHelper模块的同名接口，用于直接读取dsb文件
* CTA策略新增一个stra_get_last_exittime用于获取上一个出场信号
* WtBeEngine和WtCtaOptimizer两个模块都增加了对C++策略的支持
* 回测框架增加对session开始和结束事件的响应接口
* 监控服务：增加了查看和修改入口脚本的接口/qrygrpentry、/cmtgrpentry
* web-ui：去掉vue-json-viewer库，改用codemirror，用于展示和编辑代码
* web-ui：控制台新增入口代码修改的组件，用于修改组合盘下的run.py入口文件
* web-ui：优化了一些展示的细节
* wtpy.apps下添加了一个datahelper子模块，该模块的主要作用就是将不同数据源的数据按照WonderTrader支持的格式保存起来

### 0.6.2
* C++底层更新到2021/03/17发布的v0.6.2版本
* 日志信息翻译成英文
* webui的部分表格添加了排序和统计功能