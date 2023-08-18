from wtpy.apps import WtCtaOptimizer

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    
    optimizer = WtCtaOptimizer(8)

    optimizer.analyze(markerfile="strategies.json")

    kw = input('press any key to exit\n')
