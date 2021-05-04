from slack import WebClient
import os


def send_message(message):
    client = WebClient(token=os.environ['SLACK_API_TOKEN'])
    try:
        client.chat_postMessage(
            channel='#vaccinefinder',
            text=f"<!channel> {message}")
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")
