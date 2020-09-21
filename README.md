# wtpy
这是wonder trader针对python3适配的子框架

# wtpy子框架简介
+ wrapper子模块
	> 该模块主要包含了所有和C++底层对接的接口模块
	> - WtBtWrapper.py	主要用于和回测引擎C++核心模块对接
	> - WtDtWrapper.py	主要用于和数据组件C++核心模块对接
	> - WtExecApi.py	主要用于和C++独立执行模块对接
	> - WtWrapper.py	主要用于和实盘交易引擎C++核心模块对接
+ monitor子模块
	> 该模块主要包含了内置的监控服务，提供了Http和websocket两种连接方式
	> - DataMgr.py	主要用于读取并缓存组合数据
	> - EventReceiver.py	主要用于在指定的udp端口接收组合转发的各种事件
	> - PushSvr.py	主要用于向web提供websocket服务
	> - WatchDog.py	主要用于自动调度服务端的进程
	> - WtMonSvr.py	监控服务核心服务模块 ，利用flask实现了一个http服务接口
	> - static		webui静态文件
+ 其他模块
	> 主要位于根节点下，包含了各个子模块的入口组件
	> - WtCoreDefs.py	主要定义的Py版本的策略基类，方便用户重写
	> - CodeHelper.py 品种代码辅助模块，内置了一些方法，方便使用
	> - ContractMgr.py 合约管理器模块，用于加载contracts.json或stocks.json文件，并提供查询方法
	> - CtaContext.py	主要定义了CTA策略的上下文，可以理解为单策略的运行环境
	> - HftContext.py	主要定义了HFT策略的上下文，可以理解为单策略的运行环境
	> - SelContext.py	主要定义了SEL策略的上下文，可以理解为单策略的运行环境
	> - ExtToolDefs.py	扩展模块定义文件，主要定义了一些扩展模块的基础接口
	> - ProductMgr.py	品种管理器，主要用于Py环境中的合约属性、品种属性查询
	> - SelContext.py	选股策略上下文，即选股策略直接交互的API
	> - SessionMgr.py	交易时间模板管理器，主要用于Py环境中的交易时段模板管理
	> - StrategyDefs.py	各引擎策略基础定义模块，定义了CTA、HFT、SEL三种策略基类
	> - WtBtAnalyst.py	回测分析模块，主要是利用回测生成的数据，计算各项回测指标，并输出到excel文件
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
* XTP实盘适配，主要是修复bug

### 0.3.6
* 执行器使用线程池，减少对网络线程的时间占用
* 增加了一个实盘仿真模块TraderMocker，可以满足目前已经支持的股票和期货的仿真交易
* 更多接口支持（飞马、tap、CTPMini）
* 内置执行算法增加TWAP
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