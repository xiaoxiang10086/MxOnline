import requests
import json

def send_single_sms(apikey, code, mobile):
    #发送单条短信
    url = "https://sms.yunpian.com/v2/sms/single_send.json"
    text = "【慕学生鲜】您的验证码是{}。如非本人操作，请忽略本短信".format(code)

    res = requests.post(url, data={
        "apikey": apikey,
        "mobile": mobile,
        "text": text
    })
    re_json = json.loads(res.text)
    re_json["code"] = 0         #模拟发送成功!
    return re_json


if __name__ == "__main__":
    res = send_single_sms("d6c4ddbf50ab36611d2f52041a0b949e", "123456",          "18782902568")
    import json
    res_json = json.loads(res.text)
    code = res_json["code"]
    msg = res_json["msg"]
    if code == 0:
        print("发送成功")
    else:
        print("发送失败: {}".format(msg))
    print(res.text)