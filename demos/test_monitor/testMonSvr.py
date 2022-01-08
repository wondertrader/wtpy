from wtpy.monitor import WtMonSvr

svr = WtMonSvr(deploy_dir="E:\\deploy")
svr.run(port=8099, bSync=False)
input("press enter key to exit\n")