from datetime import datetime
from django.shortcuts import redirect, render
from config.africastalkings import send_transaction_message_response_to_reciever_phone, send_transaction_message_response_to_sender_phone
from transaction.models import Transaction
from transaction.transaction_id import generate_transaction_code_id
from users.models import Account
# from config.PTC_MPESA.lipa_na_mpesa_online import lipa_na_mpesa

from wallet.models import Wallet
from wallet.mpes.lipa_na_mpesa_online import lipa_na_mpesa

# Create your views here.
def top_up(request):
    if request.method == "POST":
        ammount = request.POST.get("ammount")
        phone = request.POST.get("phone")

        # lipa_na_mpesa(phone_number=254713303092,ammount="1")
        
        lipa_na_mpesa(phone_number=phone,ammount=ammount)
        

        print(ammount)
        def get_wallet_balance():
            wallet = Wallet.objects.filter(user_id=request.user.id)
            for wallet in wallet:
                wallet_balance =  wallet.account_balance
                return wallet_balance
        wallet_balance=get_wallet_balance()
        print(wallet_balance)
        updated_balance = int(wallet_balance) + int(ammount)

        Wallet.objects.filter(user_id=request.user.id).update(account_balance=updated_balance)

        #Succes Modals
        return redirect("success/?ammount="+ammount)
        
    return render(request,'parent/top_up.html')


def top_up_success(request):
    ammount = request.GET.get("ammount")
    print(ammount)
    def get_wallet_balance():
            wallet = Wallet.objects.filter(user_id=request.user.id)
            for wallet in wallet:
                wallet_balance =  wallet.account_balance
                return wallet_balance
    wallet_balance=get_wallet_balance()
    data = {
        "ammount" : ammount,
        "wallet_balance":wallet_balance
    }
    return render(request,'parent/top_up_success.html',data)




def transfer_cash(request,reciever_id):
    transaction = Transaction.objects.all()
    users = Account.objects.all()
    def get_user_details():
        for user in users:
            if user.id == reciever_id:
                return user

    def get_balance():
        wallet = Wallet.objects.all()
        for b in wallet:
            if b.user_id == reciever_id:
                balance = b.account_balance
                return balance
    if request.method == 'DELETE':
        response = Account.objects.filter(id=reciever_id).delete()
        return respone
    if request.method == 'POST':
        #Get post data from the sender 
        sender_id = request.user.id
        sender = Account.objects.filter(id=sender_id)
        reciever = reciever_id
        ammount = request.POST.get("ammount")
        procedure = request.POST.get("procedure")
        print(sender)
        #geting the sender name
        try:
            sender  = Wallet.objects.get(user_id = sender_id)
        except Wallet.DoesNotExist:
            sender = None
        print(sender)
        #getting phone number of the sender
        sender_phone_number = sender.user.phone_number
        print(f'Sender Phone Number : {sender_phone_number}')
        sender_name_c = request.user.user_name
        
        #geting the reciever name
        receiver  = Wallet.objects.get(user = reciever)

        # from config.PTC_MPESA.lipa_na_mpesa_online import lipa_na_mpesa
        print("senderphone",sender_phone_number)
        # lipa_na_mpesa(phone_number=sender_phone_number)
        
        #getting phone number of the reciever
        receiver_phone_number = receiver.user.phone_number
        receiver_name_c = f'{receiver.user.user_name}'
        print(receiver_name_c)
        print(f'Receiver Phone Number : {receiver_phone_number}')

        if sender.account_balance >= int(ammount):
            
            
            users = Account.objects.filter(id=reciever)
            
            receiver = Wallet.objects.get(user = reciever_id)
            #Updating the balance of the reciever after reciving the cash in the account
            receiver_balance = receiver.account_balance + int(ammount)
            print("Receiver Balalance :"+str(receiver_balance))

            #Updating the balance of the sender after successful send the ammount to the reciever
            sender_balance = sender.account_balance - int(ammount)
            print("Sender Balance :"+str(sender_balance))

            transaction_date = sender.updated_at.strftime("%d/%m/%Y")
            transaction_time = sender.updated_at.strftime("%H:%M")
            print(transaction_time)
            print(transaction_date)
                
            #Update sender Query
            Wallet.objects.filter(user=sender_id).update(account_balance=sender_balance)
                
            #Update reciever Query
            Wallet.objects.filter(user=reciever_id).update(account_balance=receiver_balance)
            transaction_id=generate_transaction_code_id()

            # transaction = Transaction(
            #     sender=Account.objects.filter(id=sender_id),
            #     transaction_id=transaction_id,
            #     reciever = Account.objects.filter(id=reciever_id),
            #     user = Account.objects.filter(id=sender_id),
            #     ammount = ammount,
            #     )
            # transaction.save()
            respone = send_transaction_message_response_to_reciever_phone(
            transaction_id = transaction_id,
            phone_number= receiver_phone_number,
            sender_name = sender_name_c,
            reciever_name = receiver_name_c,
            amount = ammount,
            date = datetime.now().strftime('%Y%m%d'),
            time = datetime.now().strftime('%Y%m%d'),
            balance = receiver_balance,
            )
            print(respone)
            send_transaction_message_response_to_sender_phone(
                  transaction_id = transaction_id,
                  phone_number = sender_phone_number,
                  sender_name = sender_name_c,
                  reciever_name = receiver_name_c,
                  amount = ammount,
                  date = datetime.now().strftime('%Y%m%d'),
                  time = datetime.now().strftime('%Y%m%d'),
                  balance = sender_balance,)
            print("Done")
    data = {
        "balance" : get_balance(),
        "user":get_user_details(),
    }
    return render(request,'child/child_top_up.html',data)              
                

def child_withdraw(request):
    if request.method == 'POST':
        ammount = request.POST.get("ammount")
        phone = request.POST.get("phone")
        reason = request.POST.get("reason")
        print(ammount)
        print(phone)
        print(reason)
        user_id = request.user.id
        wallet = Wallet.objects.filter(user_id=user_id)
        for wallet in wallet:
            wallet_balance =  wallet.account_balance
        if int(ammount) <= int(wallet_balance):
            updated_balance = int(wallet_balance) - int(ammount)
            Wallet.objects.filter(user_id=request.user.id).update(account_balance=updated_balance)
            return redirect("success/?ammount="+ammount)
        else:
            return redirect("error_withdraw/?ammount="+ammount)
    return render(request,'child/child_withdraw.html')

def withdraw_success(request):
    ammount = request.GET.get("ammount")
    def get_wallet_balance():
            wallet = Wallet.objects.filter(user_id=request.user.id)
            for wallet in wallet:
                wallet_balance =  wallet.account_balance
                return wallet_balance
    wallet_balance=get_wallet_balance()
    data = {
        "ammount" : ammount,
        "wallet_balance":wallet_balance
    }
    return render(request,'child/withdraw_success.html',data)

