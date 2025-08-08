# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`
from firebase_functions import https_fn
from flask import Flask,request,g,Response
from flask_cors import CORS
from firebase_admin import firestore
from firebase_admin import auth
from firebase_admin import initialize_app
from google.cloud.firestore_v1.base_query import FieldFilter
import time
from datetime import datetime, timedelta
import json
import functions_framework
import base64
# import firebase_admin
# from firebase_admin import credentials

# cred = credentials.Certificate("./firebase-adminsdk.json")
# firebase_admin.initialize_app(cred)


initialize_app()

app = Flask(__name__, static_folder="static", static_url_path="/www")
app.json.ensure_ascii = False

CORS(app)  # 启用 CORS，允许所有域访问



@https_fn.on_request()
def pulse_monitor(req: https_fn.Request) -> https_fn.Response:
    with app.request_context(req.environ):
        return app.full_dispatch_request()
@app.before_request
def before_request():
    uid = request.args.get("uid","test_uid")
    auth_token = request.headers.get('Authorization')
    if auth_token  != None:    
        try:    
            decoded_token = auth.verify_id_token(auth_token.replace('Bearer ', ''))
            uid = decoded_token['uid']
        except:
            return "认证过期", 401
        # for k in  decoded_token:
        #     print(k,decoded_token[k])
        g.decoded_token = decoded_token
        g.auth = True
    else:
        g.auth = False
    g.uid = uid
    

@app.get("/hello")
def hello():                
    return "Hello world! "

@app.get("/get_uid")
def get_uid():
    uid = g.uid
    db = firestore.client()
    doc_ref = db.collection('user_ids').document(uid)
    doc = doc_ref.get()
    if doc.exists == False:
        data = {
            'uid': uid,
            'exp':0,
        }
        doc_ref.set(data)
        doc = doc_ref.get()
        
    if g.auth:
        n = doc.to_dict()   
        if n.get("exp",0) != g.decoded_token.get("exp",0):
            doc_ref.update(g.decoded_token)  
            doc = doc_ref.get()
    return {"state":0,"data":doc.to_dict(),"msg":""}





#支付接口 start

@app.post("/pay/get_uid")
def pay_uid():      
    server_key = request.headers.get("ServerKey")
    if server_key is None or server_key != "MXSCG08XOE":
        return "Bad Request", 400
    
    data = {"state": 0,"msg": "success", "data": { "id":g.uid }}
    return data

@app.post("/pay/callback")
def pay_callback():          
    server_key = request.headers.get("ServerKey")
    if server_key is None or server_key != "MXSCG08XOE":
        return "Bad Request", 400
          
    data = request.get_json()
    uid = data['order']['user_id']
    db = firestore.client()
    if data['type'] == "CreateOrder":        
        doc_ref = db.collection("pay_detail").document(data['order']['order_id'])
        doc_ref.set(data)
        
    elif data['type'] == "RenewalCreateOrder":
        doc_ref = db.collection("pay_detail").document(data['order']['order_id'])
        doc_ref.set(data)
    elif data['type'] == "Refund":
        doc_ref = db.collection("pay_detail").document(data['order']['order_id'])
        doc_ref.update(data)
        
    if data['member_rights']:
        doc_ref = db.collection('user_ids').document(uid)
        doc = doc_ref.get()

        data = {
            'uid': uid,
            'member_rights': data['member_rights']
        }
        if doc.exists:
            doc_ref.update(data)
        else:
            doc_ref.create(data)
    
    return {"state": 0,"msg": "success"}

#支付接口 end



@app.get("/server_config/get")
def getGameConfigData():
    db = firestore.client()
    doc_ref = db.collection("server_config")
    doc_ref = doc_ref.document("server_config")
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        return {"state":0,"data":data,"msg":""}
    return {"state":0,"data":{},"msg":""}



@app.post("/server_config/update")
def updateGameConfigData():
    db = firestore.client()
    doc_ref = db.collection("server_config").document("server_config")
    data = request.get_json()
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update(data)
    else:
        doc_ref.set(data)
    return {"state":0,"data":{},"msg":""}




@app.get("/trigger_wokrer")
def trigger_wokrer():
    import recall_email
    from datetime import datetime, timedelta

    current_date = datetime.now()
    seven_days_ago = current_date - timedelta(days=7)
    db = firestore.client()
    doc_ref = db.collection('user_ids').where(filter=FieldFilter("email_verified", "==",True))
    doc_ref = doc_ref.where(filter=FieldFilter("create_time", "<",seven_days_ago.strftime("%Y-%m-%d %X")))
    # doc_ref = doc_ref.where(filter=FieldFilter("member_rights", "==",None ))
    docs = doc_ref.get()
    count  = 0
    pass_email = 0
    for doc in docs:
        data = doc.to_dict()
        email = data.get("email")
        create_time = data.get("create_time")
        if "privaterelay.appleid.com"  in email:
            continue
        
        if data.get("member_rights"):
            pass_email += 1
            continue
        else:
            recall = data.get("re_call")
            if recall:
                continue
              
        try:
            
            doc_ref = db.collection('user_ids').document(doc.id)
            doc = doc_ref.get()
            doc_ref.update({"re_call":time.strftime("%Y-%m-%d %X",time.localtime())})   
            
            recall_email.send_recall_email(email)
        except:
            print("发召回邮件失败") 
        
            
        print(doc.id,email,create_time)
        count += 1
        
    print(seven_days_ago.strftime("%Y-%m-%d %X"),count,pass_email)
    
    return {"state":0,"data":{},"msg":""}



@app.get("/download_email")
def download_email():
    db = firestore.client()
    doc_ref = db.collection('user_ids').where(filter=FieldFilter("email_verified", "==",True))
    docs = doc_ref.get()
    
    f = open('email.txt', 'w')
    
    for doc in docs:
        data = doc.to_dict()
        email = data.get("email")
        if "privaterelay.appleid.com"  in email:
            continue
        
        if data.get("member_rights"):
            continue
        f.write(email+"\n")
        
    f.close()
    return {"state":0,"data":{},"msg":""}


@app.route('/get_user_group', methods=['GET'])
def get_user_group():
    data = {
        "task_groups":[{
            "group_type":1,
            "group_desc":"指定用户"
        },{
             "group_type":2,
            "group_desc":"发送给全员"
        },{
             "group_type":3,
            "group_desc":"7天未登录"
        }]
    }
    return {'status': 'OK', 'description': '','data':data}


@app.route('/commit_email_task', methods=['POST'])
def commit_email_task():
    from google.cloud import pubsub_v1
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path('caloriescan', 'email-tasks')
    
    data = request.get_json()
    task_id = data.get('task_id', '')
    task_name = data.get('task_name', '')
    user_group_type = data.get('user_group_type', 1)
    receive_emails = data.get('receive_emails','')
    task_content = data.get('task_content','')
    task_subject = data.get('task_subject','')
    total_user = 0
    if user_group_type == 1:
        if not receive_emails:
            return {'status': 'ERROR', 'description': '指定用户组时，接收用户不能为空'}
        emails = receive_emails.split(',')
        message = {
            "subject":task_subject,
            "content":task_content,
            "task_id": task_id,
            "user_group_type":user_group_type,
            "task_name": task_name,
            "receive_emails":emails
        }
        publisher.publish(topic_path, data=json.dumps(message).encode('utf-8'))
    elif user_group_type == 2:
        # 全员发送，暂时不处理
        db = firestore.client()
        doc_ref = db.collection('user_ids').where(filter=FieldFilter("email_verified", "==",True))
        docs = doc_ref.get()
        emails = []
        i = 0
        for doc in docs:
            info = doc.to_dict()
            email = info.get("email")
            if "privaterelay.appleid.com"  in email:
                continue
            if email == "":
                continue
            emails.append(email)
            i  += 1
            total_user += 1
            if i < 100:
                continue
            message = {
                "subject":task_subject,
                "content":task_content,
                "task_id": task_id,
                "task_name": task_name,
                "user_group_type":user_group_type,
                "receive_emails":emails
            }
            publisher.publish(topic_path, data=json.dumps(message).encode('utf-8'))
            i = 0
            emails = []
        if len(emails) > 0:
            message = {
                "subject":task_subject,
                "content":task_content,
                "task_id": task_id,
                "user_group_type":user_group_type,
                "task_name": task_name,
                "receive_emails":emails
            }
            publisher.publish(topic_path, data=json.dumps(message).encode('utf-8'))
    elif user_group_type == 3:
        db = firestore.client()
        doc_ref = db.collection('user_ids').where(filter=FieldFilter("email_verified", "==",True))
        docs = doc_ref.get()
        emails = []
        i = 0
        for doc in docs:
            info = doc.to_dict()
            email = info.get("email")
            last_login = info.get("last_login")
            if last_login is not  None and last_login != "":
                last_login_date = datetime.strptime(last_login, "%Y-%m-%d")
                if (datetime.now() - last_login_date).days < 7:
                    continue            
            if "privaterelay.appleid.com"  in email:
                continue
            if email == "":
                continue
            emails.append(email)
            i  += 1
            total_user += 1
            if i < 100:
                continue
            message = {
                "subject":task_subject,
                "content":task_content,
                "task_id": task_id,
                "task_name": task_name,
                "user_group_type":user_group_type,
                "receive_emails":emails
            }
            publisher.publish(topic_path, data=json.dumps(message).encode('utf-8'))
            i = 0
            emails = []
        if len(emails) > 0:
            message = {
                "subject":task_subject,
                "content":task_content,
                "task_id": task_id,
                "user_group_type":user_group_type,
                "task_name": task_name,
                "receive_emails":emails
            }
            publisher.publish(topic_path, data=json.dumps(message).encode('utf-8'))
        
    #todo 保存发送记录
    db = firestore.client()
    doc_ref = db.collection('send_email_detial').document(task_id)
    doc = doc_ref.get()
    if doc.exists == False:
        data["total_user"] = total_user
        doc_ref.set(data)

    return {'status': 'OK', 'description': ''}



@app.route('/get_email_task', methods=['GET'])
def get_email_task():
    # // 0 任务已提交 还未开始 1 进行中 2 已完成
    task_id = request.args.get('task_id', '')
    data = {
        "task_id": task_id,
        "task_name": "测试任务",
        "task_state": 2,  # 0 任务已提交 还未开始 1 进行中 2 已完成  
    }
    return {'status': 'OK', 'description': '','data':data}





@app.route('/send_batch_email', methods=['POST'])
def send_batch_email():
    from google.cloud import pubsub_v1
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path('caloriescan', 'email-tasks')
    emails = request.json.get('emails', [])
    for email in emails:
        publisher.publish(topic_path, data=json.dumps(email).encode('utf-8'))
    return {'state': 0, 'msg': '任务已提交'}



@functions_framework.cloud_event
def send_email_worker(cloud_event):
    """
    Cloud Function 入口点 - 处理 Pub/Sub 消息并发送邮件
    
    Args:
        cloud_event: Cloud Event 对象，包含 Pub/Sub 消息
    """
    try:
        # 解析 Pub/Sub 消息
        pubsub_message = cloud_event.data["message"]
        # 获取消息数据（Base64 编码的字符串）
        message_data = pubsub_message["data"]
        # 解码消息数据
        decoded_data = base64.b64decode(message_data).decode('utf-8')
        # 解析 JSON 数据
        email_data = json.loads(decoded_data)
        print("send_email_worker message ",email_data)
            
        # 获取邮件内容和收件人地址
        subject = email_data.get("subject", "默认主题")
        content = email_data.get("content", "默认内容")
        receive_emails = email_data.get("receive_emails", [])
        user_group_type = email_data.get("user_group_type", 0)
        
        if not receive_emails:
            print("没有接收邮件地址，跳过发送")
            return
        
        # 发送邮件
        for email_address in receive_emails:
            # if user_group_type != 1:
            #     print(f"pass user_group_type {user_group_type} {email_address} ")
            #     continue
            try:
                if not email_address:
                    continue
                r = send_email.send_worker_email(email_address, subject, content)
                print(f"已发送邮件到: {email_address} {r}")
            except Exception as e:
                print(f"处理邮件地址时发生错误: {str(e)}")
                continue
    except Exception as e:
        print(f"处理邮件任务时发生错误: {str(e)}")
        # 抛出异常会让 Pub/Sub 重试
        raise e
