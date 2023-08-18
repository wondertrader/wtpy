from wtpy import WtDtServo

dtServo = WtDtServo()

def test_future():
    dtServo.setBasefiles(folder="../common/")
    dtServo.setStorage(path='../storage/')

    # 读取IF主力合约的前复权数据
    bars = dtServo.get_bars("CFFEX.IF.HOT-", "m5", fromTime=202205010930, endTime=202205281500).to_df()
    bars.to_csv("CFFEX.IF.HOT-.csv")

    # 读取IF主力合约的后复权数据
    bars = dtServo.get_bars("CFFEX.IF.HOT+", "m5", fromTime=202205010930, endTime=202205281500).to_df()
    bars.to_csv("CFFEX.IF.HOT+.csv")

    # 读取IF主力合约的原始拼接数据
    bars = dtServo.get_bars("CFFEX.IF.HOT", "m5", fromTime=202205010930, endTime=202205281500).to_df()
    bars.to_csv("CFFEX.IF.HOT.csv")

    # 读取IF主力合约的tick数据
    bars = dtServo.get_ticks("CFFEX.IF.HOT", fromTime=202207250930, endTime=202207291500).to_df()
    bars.to_csv("CFFEX.IF.HOT_ticks.csv")

def test_futopt():
    dtServo.setBasefiles(folder="../common/", commfile="fopt_comms.json", contractfile="fut_options.json")
    dtServo.setStorage(path='D:/data_fopt/')

    # SHFE.au2308C448
    bars = dtServo.get_bars("SHFE.au2308.C.448", "m5", fromTime=202205010930, endTime=202308181500)
    if bars is not None:
        print(bars.to_df()[:100])
        
    # DCE.i2309-C-800
    bars = dtServo.get_bars("DCE.i2309.C.800", "m5", fromTime=202205010930, endTime=202308181500)
    if bars is not None:
        print(bars.to_df()[:100])

    # CZCE.TA309C6000
    bars = dtServo.get_bars("CZCE.TA2309.C.6000", "m5", fromTime=202205010930, endTime=202308181500)
    if bars is not None:
        print(bars.to_df()[:100])

    ###############################################################################################
    # 以下是读取tick数据的示例
    # SHFE.cu2309C68000
    ticks = dtServo.get_ticks_by_date("SHFE.cu2309.C.68000", 20230818)
    if ticks is not None:
        print(ticks.to_df()[:100])

    ticks = dtServo.get_ticks("SHFE.cu2309.C.68000", fromTime=202308180900, endTime=0)
    if ticks is not None:
        print(ticks.to_df()[:100])

    # DCE.i2310-C-850
    ticks = dtServo.get_ticks_by_date("DCE.i2310.C.850", 20230818)
    if ticks is not None:
        print(ticks.to_df()[:100])

    # CZCE.MA405C2425
    ticks = dtServo.get_ticks_by_date("CZCE.MA2405.C.2425", 20230818)
    if ticks is not None:
        print(ticks.to_df()[:100])

test_futopt()