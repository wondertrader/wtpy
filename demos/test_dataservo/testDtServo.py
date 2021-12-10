from wtpy.wrapper import WtDtServo

dtServo = WtDtServo()
dtServo.setBasefiles(folder="../common/")
dtServo.setStorage("../FUT_DATA/")
dtServo.commitConfig()


bars = dtServo.get_bars(stdCode = "CFFEX.IC.HOT", period = "m5", fromTime = 202107010930, endTime = 202107211500)
print(len(bars))
bars = dtServo.get_bars(stdCode = "CFFEX.IC.HOT", period = "m15", fromTime = 202107010930, endTime = 202107211500)
print(len(bars))

bars = dtServo.get_bars(stdCode = "CFFEX.IC.HOT", period = "m1", dataCount = 500, endTime = 202107211500)
print(len(bars))
bars = dtServo.get_bars(stdCode = "CFFEX.IC.HOT", period = "m3", dataCount = 150, endTime = 202107211500)
print(len(bars))

ticks = dtServo.get_ticks(stdCode = "CFFEX.IC.HOT", dataCount = 500, endTime = 202107221500)
print(len(ticks))

ticks = dtServo.get_ticks(stdCode = "CFFEX.IC.HOT", fromTime = 202107210930, endTime = 202107221500)
print(len(ticks))
    