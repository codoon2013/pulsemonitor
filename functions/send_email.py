# -*- coding:utf-8 -*-
import resend
resend.api_key = "re_8bsrLLg1_NU1XMLDwFKBg2BF5zySQxG7v"


def send_worker_email(email_address,subject,html):
  params = {
    "from": "CalorieScan <CalorieScan@fitboxapp.net>",
    "to": [email_address],
    "subject": subject,
    "html": html,
  }
  r = resend.Emails.send(params)
  return r
  
  

def send_email(email_address="155214685@qq.com"):
  if email_address == "":
    return

  '''定义主题'''
  Subject = 'Welcome to CalorieScan - Your Journey to Effortless Diet Management Begins Now!'

  html = register_conent
  
  params = {
    "from": "CalorieScan <CalorieScan@fitboxapp.net>",
    "to": [email_address],
    # "reply_to":"liaosong@codoon.com",
    "subject": Subject,
    "html": html,
  }
  email = resend.Emails.send(params)
  print(email)


register_conent  = '''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0" />
    <title></title>
    <title></title>
    <script>
      function setBaseFontSize(){
         var baseSize = 16; 
         var deviceWidth = document.documentElement.clientWidth || window.innerWidth;
         if (deviceWidth > 480) return
            var scale = deviceWidth / 375;
            document.documentElement.style.fontSize = `${baseSize * scale}px`;
        };
      window.onload=function(){
        setBaseFontSize();
        window.addEventListener('resize', setBaseFontSize);
      }
    </script>
    <style>
      body{
        margin:0px !important;
      }
      .page{
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100vw;
      }
      @media (min-width:481px) {
        .content{
          width: 500px!important;
        }
        .icon1{
           width: 183px!important;
         }
       .icon2{
          width:122px!important;
         }
      }
      .content{    
        width:23.4375rem;
        display: block;
        padding-bottom: 1.4375rem;
      }
      .cover{
        width: 100%;
        height: auto;
        display: block;
      }
      .bottom-div{
        margin-top: 0.75rem;
        padding: 0 6% 0 5%;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .icon1{
        width: 8.625rem;
        height: auto;
        display: block;
      }
      .icon2{
        width: 5.6875rem;
        height: auto;
        display: block;
      }
    </style>
  </head>
  <body>
   <div class="page">
    <div class="content">
      <img class="cover" src="https://firebasestorage.googleapis.com/v0/b/caloriescan.appspot.com/o/v2%2Fone1.png?alt=media"/>
      <img class="cover" src="https://firebasestorage.googleapis.com/v0/b/caloriescan.appspot.com/o/v2%2Fone2.png?alt=media"/>
      <div class="bottom-div">
        <img class="icon1" src="https://firebasestorage.googleapis.com/v0/b/caloriescan.appspot.com/o/v2%2Flogo.png?alt=media"/>
         <a class="icon2" href="https://apps.apple.com/us/app/caloriescan/id6502442511?l=zh-Hans-CN" target="_blank">
        <img class="icon2" id="downloadbtn" src="https://firebasestorage.googleapis.com/v0/b/caloriescan.appspot.com/o/v2%2Fdownload.png?alt=media"/>
       </a> 
       </div>
    </div>
   </div>
  </body>
</html>'''