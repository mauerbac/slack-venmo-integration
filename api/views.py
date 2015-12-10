from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from api.models import NumberMap, Requestor
import json, requests

#Oauth endpoint for Venmo
def venmoauth(request):
    code = request.GET.get('code')

    # parse slack_id and slack_username
    params = request.GET.get('params').split("@@@")
    slack_id = params[0]
    slack_username = params[1]

    # prepare payload Oauth request for Venmo
    # supply Venmo Client_ID, Client_Secret, short-lived Code
    payload = {
    "client_id": "ClIENT_ID",
    "client_secret": "CLIENT_SECRET",
    "code": code
    }

    # exchange short-lived code for access token
    url = "https://api.venmo.com/v1/oauth/access_token"

    response = requests.post(url, payload)
    # parse Venmo response
    response_dict = response.json()

    # receive venmo token & phone number
    venmo_token = response_dict['access_token']
    venmo_number = response_dict['user']['phone']

    # if successful Oauth register user
    if not is_authenticated(slack_id):
        new_user = Requestor(slack_user_id=slack_id, venmo_auth_token=venmo_token)
        new_user.save()

    # also, add user to mappings to venmo
    if not NumberMap.objects.all().filter(slack_username=slack_username).exists():
        new_mapping = NumberMap(phone_number=venmo_number, slack_username=slack_username)
        new_mapping.save()

    return redirect('/web/success')

# slack doesn't send a CSRF token -- ignoring for now
@csrf_exempt
def main(request):
    # parse data from Slack's request
    # view format in "Triggering a Command"
    # -> https://api.slack.com/slash-commands
    data = request.POST

    # recieve slack_username & slack_id
    slack_username = data['user_name']
    slack_id = data['user_id']
    slack_token = data['token']

    # check for Slack token
    # supply your team's token
    if slack_token != 'SLACK_TEAM_TOKEN':
        return send_response('Something went wrong. :(')

    # Oauth URL for Venmo
    auth_msg = 'You haven\'t used this app yet. Authenticate with Venmo <https://api.venmo.com/v1/oauth/authorize?client_id=3284&scope=make_payments%20access_phone&response_type=code&redirect_uri=http://52.11.216.237:8000/api/venmoauth?params={0}@@@{1}| here> first. '.format(slack_id, slack_username)
    
    msg = ''

    # warn user if not authenticated with Venmo
    if not is_authenticated(slack_id):
        msg = auth_msg

    # parse text
    try:
        # parse the command's body
        slack_text = data['text'].split()

        if slack_text[0] == 'help':
            msg += 'To make a payment: `/slackmo [@username] [$amount] [note]` ex: /slackmo @mauerbac $10 lunch . '
            return send_response(msg)

        elif slack_text[1] == 'add':
            return add_user_mapping(slack_text)

        elif slack_text[1][0] == '$':
            return make_payment(slack_text, auth_msg, slack_id)

    except IndexError:
        return send_response(msg + 'Invalid command. Try `/slackmo help`. ')

# send response back to slack
def send_response(message):
    response_data = {}
    response_data['text'] = message
    return HttpResponse(json.dumps(response_data), content_type="application/json")

# check if user is authenticated with Venmo
def is_authenticated(slack_id):
    return Requestor.objects.all().filter(slack_user_id=slack_id).exists()

# add user to NumberMap
def add_user_mapping(slack_text):
    number = str(slack_text[2])
    receiver_username = slack_text[0].strip("@")

    if NumberMap.objects.all().filter(slack_username=receiver_username).exists():
        return send_response('{0} has already been added. Make your payment now!'.format(receiver_username))

    else:
        new_mapping = NumberMap(phone_number=number, slack_username=receiver_username)
        new_mapping.save()
        return send_response('{0} has been added to Slackmo. Make your payment now!'.format(receiver_username))

# process Venmo payment
def make_payment(slack_text, auth_msg, slack_id):

    receiver_username = slack_text[0].strip("@")

    # ensure user has a Venmo auth token
    if not is_authenticated(slack_id):
        return send_response(auth_msg)

    if NumberMap.objects.all().filter(slack_username=receiver_username).exists():

        amount = slack_text[1]
        message = " ".join(slack_text[2:])

        # retrieve auth token for current user & receiver's number
        auth_token = Requestor.objects.get(slack_user_id=slack_id).venmo_auth_token
        to_number = NumberMap.objects.get(slack_username=receiver_username).phone_number
        amount_format = amount.strip("$")

        # build payload
        payload = {
            'access_token': str(auth_token),
            'phone': str(to_number),
            'note' : message,
            'amount': amount_format,
            'audience' : 'public'
        }

        # make payment!
        response = requests.post("https://api.venmo.com/v1/payments", payload).json()

        # check for any errors and alert user
        if 'error' in response:
            return send_response('There was an error on the Venmo side')
        else:
            return send_response('You paid {0} {1} for {2}!'.format(receiver_username, amount, message))
    else:
        return send_response('{0} has not used Slackmo yet :(. Please add his phone number. Using `/slackmo @username add [number]` 10 digit number ex: 19145550000'.format(receiver_username))
