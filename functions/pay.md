支付接口

校验 key MXSCG08XOE

正式地址

1 获取会员 uid
方法 post json
接口 https://pulse-monitor-qaw2fmr7bq-uc.a.run.app/pay/get_uid
返回 {"data":{"id":"test_uid"},"msg":"success","state":0}

2 支付回调
方法 post json
接口 https://pulse-monitor-qaw2fmr7bq-uc.a.run.app/pay/callback
返回 {"state": 0,"msg": "success"}
