## pip install gspread oauth2client
## pip install twilio
## pip install Flask

import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials 
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import re

Name_col = 1
Number_col = 2
Permissions_col = 3
Generic_col = 4
Picnic_col = 5
Fivek_col = 6
Onam_col = 7
Chistmas_col = 8
Event_Col = Picnic_col
Picnic_Mess_Yes = "Thanks for responding.We will see you at the Pinic. if you need directions click on this link https://goo.gl/maps/RuKXhofcruS2 "
Picnic_Mess_No = "We are sorry that you will be unable to attend the picnic." + \
            " If you change your mind let us know by replying 'Y' or 'Yes'." 
FiveK_Mess_Yes = "Thanks for responding. We will see you at the 5K Event.."
FiveK_Mess_No = "We are sorry that you will be unable to attend 5K event." + \
            " If you change your mind let us know by replying 'Y' or 'Yes'." 
Onam_Mess_Yes = "Thanks for responding. We will see you at the Onam function."
Onam_Mess_No = "We are sorry that you will be unable to attend the Onam function." + \
            " If you change your mind let us know by replying 'Y' or 'Yes'."
Christmas_Mess_Yes = "Thanks for responding. We will see you at the Christmas Event.."
Christmas_Mess_No = "We are sorry that you will be unable to attend the Christmas event." + \
            " If you change your mind let us know by replying 'Y' or 'Yes'."
			
def get_worksheet_link():
    try:
        scope = ['https://spreadsheets.google.com/feeds']
        creds = ServiceAccountCredentials.from_json_keyfile_name('My Project-49d1c751ac48.json', scope)
        client = gspread.authorize(creds)
   #     sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1hbMfs0wQCLz7NumJUBKfUD8G28jxIfHdg6KiZbdPskw/edit?usp=sharing')
        sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1p-i4OxTFU6MSc7V5V208RHFYbea470oLfTL8tn8_h0s/edit?usp=sharing')
        worksheet = sheet.get_worksheet(0)
        return(worksheet)
    except:
        return(False)
    
def get_response_text(messtype):
    curr_text_message = ''
    if (Event_Col == 4):        
            curr_text_message = "This is the KAKC notification system. Please visit KAKC.org if you would " + \
            "like to learn more about our organization."         
    elif (Event_Col == 5):
        if (messtype == 1):
            curr_text_message = Picnic_Mess_Yes
        else:
            curr_text_message = Picnic_Mess_No
    elif (Event_Col == 6):
        if (messtype == 1):
            curr_text_message = FiveK_Mess_Yes
        else:
            curr_text_message = FiveK_Mess_No
    elif (Event_Col == 7):
        if (messtype == 1):
            curr_text_message = Onam_Mess_Yes
        else:
            curr_text_message = Onam_Mess_No
    elif (Event_Col == 8):
        if (messtype == 1):
            curr_text_message = Christmas_Mess_Yes
        else:
            curr_text_message = Christmas_Mess_No 
    return(curr_text_message)

def get_action_plan(message):
    testStr = message.strip().upper()
    if (testStr == 'Y' or testStr == 'YES'):
        return(1)
    elif (testStr == 'N' or testStr == 'NO'):
        return(2)
    elif (testStr == 'JOIN') or (testStr == 'START'):
        return(3)
    elif (testStr == 'STOP') or (testStr == 'REMOVE'):
        return(4)
    elif (testStr == 'PAUSE'):    
        return(5)
    elif (testStr == 'INFO'):    
        return(10)
    else:
        return(100)
    
def update_response_in_gsheet(phonenumber,worksheet1,body,path2):          
    try:        
        records = worksheet1.find(phonenumber)               
        message  = "Hi " + worksheet1.cell(records.row,1).value + ', ' + get_response_text(path2)  
        if (path2==1):            
            worksheet1.update_cell(records.row,Event_Col,'Yes')
        else:            
            worksheet1.update_cell(records.row,Event_Col,'No')
        return(message)
    except:
        message = "Hi {}, We are unable to locate you in KAKC system.".format(phonenumber) + \
        "Reply 'Y' or 'Yes' if you want to be added to our notification system. " + \
        "Reply 'N' or 'No' to be exluded. "
        newrow = ['Unkown',phonenumber,'Asked']
        newrowcount = worksheet.row_count+1
        print(newrowcount)
        worksheet.append_row(newrow)
        
	def check_number_and_permissions(worksheet1,number1,message1):
    resp1 = ''
    try:       
        records = worksheet1.find(number1)  
        currstatus = worksheet1.cell(records.row, Permissions_col).value.strip()
        plan1 = get_action_plan(message1)
        print(currstatus)
        print(plan1)
        if (currstatus == 'Asked'):
            if (message1.strip().upper() == 'Y') or (message1.strip().upper() == 'Y'):
                    resp1 = 'Thank you for your response. You will be included in all future notifications.'
                    worksheet1.update_cell(records.row,Permissions_col,'Text')
            else:
                    resp1 = "Thank you for your response.You can always enroll in th future by texting 'Y' to this number."
                    worksheet1.update_cell(records.row,Permissions_col,'No')
            return(False,resp1)
        elif (currstatus == 'Text'):         
            if (plan1 == 3):                
                    resp1 = "You are already subcribed to receive notifications. Text 'Info' " + \
                    " to get KAKC information."
            elif (plan1 ==4):
                resp1 = "We are sorry to see you go. Re-subscribe anytime by texting 'Start' to this number." 
                worksheet1.update_cell(records.row,Permissions_col,'No')
            elif (plan1 == 10):
                resp1 = "This is the KAKC notification system that sends relevant updates to KAKC members." + \
                " Text 'Join' to be added to list or 'Remove' to unsubcribe." 
            elif (plan1 == 5):
                resp1 = "We have paused your notifications. Text 'START' or 'RESTART' to reactivate notifications." 
                worksheet1.update_cell(records.row,Permissions_col,'Paused')                
            else:
                return(True,'')
#                resp1 = "Sorry unable to understand. Text 'Join' to be added to list. 'Stop' to unsubcribe or 'Info'" + \
 #               " to get KAKC information."
            return(False,resp1)
        elif (currstatus == 'No'):
            if (plan1 == 3):                
                    resp1 = 'Thank you joining. You will be included in all future notifications.'
                    worksheet1.update_cell(records.row,Permissions_col,'Text')
            elif (plan1 ==4):
                resp1 = "You are not subscribed to this list. Re-subscribe anytime by texting 'Join' to this number." 
                worksheet1.update_cell(records.row,Permissions_col,'No')
            elif (plan1 == 10):
                resp1 = "This is the KAKC notification system that sends relevant updates to KAKC members." + \
                " Text 'Join' to be added to list or to unsubcribe."  
            else:
                resp1 = "Sorry unable to understand. Text 'Join' to be added to list. 'Remove' to unsubcribe or 'Info'" + \
                " to get KAKC information."               
            return(False,resp1)
        elif (currstatus == 'Paused'):
            if (plan1 == 3):                
                    resp1 = "KAKC notifications have been reactivated. Text 'PAUSE' to pause it anytime. Text 'Remove' " + \
                    "to be removed from the system. You will need to text 'START' to reactivate."
                    worksheet1.update_cell(records.row,Permissions_col,'Text')
            elif (plan1 ==4):
                resp1 = "We are sorry to see you go. Re-subscribe anytime by texting 'Start' to this number." 
                worksheet1.update_cell(records.row,Permissions_col,'No')
            elif (plan1 == 10):
                resp1 = "This is the KAKC notification system that sends relevant updates to KAKC members." + \
                " Text 'Pause' to start receiving you notifications or 'Remove' to unsubcribe." 
            elif (plan1 == 5):
                resp1 = "We have paused your notifications. Text 'START' or 'RESTART' to reactivate notifications." 
                worksheet1.update_cell(records.row,Permissions_col,'Text')     
            return(False,resp1)
        return(True,resp1)
    except:
        newrow = ['Unkown',number1,'Asked']
        worksheet1.append_row(newrow)
        resp1 = "We don't have your number is our system. Do you want to be added to our text/voice notification system?" + \
        "Reply 'Y' or 'Join' to be added."
        print(resp1)
        return(False,resp1)
    
    return(True,'')
    
app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    number = request.values.get('From')[1:]
    number = re.sub('[!@#$+-]', '', number)
    print(number)
    message_body = request.form['Body']
    resp = MessagingResponse()
    worksheet = get_worksheet_link()
    (flag, retmess) = check_number_and_permissions(worksheet,number,message_body)
    if (flag == False):
        print(retmess)
        resp.message(retmess)
        return str(resp)
    else:
        path = get_action_plan(message_body)
        if (path==1 or path==2):                
            returnMessage = update_response_in_gsheet(number,worksheet,message_body,path)
        else:
            returnMessage = "Sorry, unable to understand the reponse. " + \
            "Please text 'Y' or 'Yes' if you are attendng and 'N' or 'No' if unable to attend. Thank you."
        print(returnMessage)
        resp.message(returnMessage)
        return str(resp)
      
    
    
if __name__ == "__main__":
    app.run()	
				
