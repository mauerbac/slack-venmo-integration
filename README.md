# Building a Venmo Integration for Slack

##Overview

[http://slackmo.elasticbeanstalk.com/](http://slackmo.elasticbeanstalk.com/)

This is a sample app leveraging Slack’s [slash command](https://api.slack.com/slash-commands) integration for Venmo. Within Slack you can easily pay your co-workers using a simple command. Currently, it supports the ability to pay using their Slack username. 

###Slash Commands

Slash Commands are a great way to get started with Slack integrations. Anytime a user initiates a slash command (`/slackmo`), Slack merely POSTs the necessary data to your provided endpoint. A sample request can be seen here:

```
token=gIkuvaNzQIHg97ATvDxqgjtO
team_id=T0001
team_domain=example
channel_id=C2147483705
channel_name=test
user_id=U2147483697
user_name=Steve
command=/weather
text=94070
response_url=https://hooks.slack.com/commands/1234/5678
```

You endpoint must parse through this data and provide a JSON response to Slack, so that it can respond back to the user. In this app, we use user_name, user_id & command to make payments on the user’s behalf. 

**Please Note**: This app requires additional consideration around security. Ideally, the user should authenticate with the app every time they attempt to make a payment. A user could spoof one another by making a POST request to my endpoint with another user’s username and pay himself. I think it defeats the purpose of a slash command if a user must authenticate each time, so I’d be curious to see if I’m missing something here. 


## Usage 

Supports 3 commands:

* `/slackmo [@username] [$amount] [note]` . For example, `/slackmo @mauerbac $10 lunch!`
* `/slackmo help`
* `/slackmo [@username] add [phone #]` - Used for adding a new co-worker

**You can request money by using a negative dollar amount. i.e $-10 


### Building the app

A first time user will be immediately prompted to Oauth with Venmo. A user must authenticate with Venmo so the app can make payments on their behalf. This token is saved in the app’s database for later use. A Slack username doesn’t necessarily map to a Venmo username, so I needed to create a mapping of Slack username to a Venmo identifying. In this app, I used the Slack username and Venmo phone number. If the receiver hasn’t used the app, you must supply their phone number using the `/slackmo @will add [number]` command. 

The app has two endpoints: `/main` & `/venmoauth’, which can be seen in `api/views.py`. Slack POSTs all slash command data to the main endpoint and Venmo uses the venmoauth endpoint in the OAuth process.   


###Housekeeping

1. Register a [custom slack command](https://my.slack.com/services/new/slash-commands).
2. Register an App with Venmo [here](https://venmo.com/account/settings/developer). Make note of Client ID & Client Secret.
3. Supply Venmo Client ID, Client Secret and Slack Token in `api/views.py`.
4. Deploy the application and provide Slack with your endpoint.
5. Give it a try!

### Next steps

* Add support to refresh Venmo Auth tokens when expired.
* Add better authentication to avoid co-worker spoofing.
* Add additional commands.
* Become an offical Slack Integration via the [Slack Button](https://api.slack.com/docs/slack-button).

Reach out to @mauerbac with questions/feedback. Thanks!
