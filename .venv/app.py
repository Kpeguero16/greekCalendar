import os
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from create_event import create_google_calendar_event

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.event("message")
def handle_message_events(body, logger):
    logger.info(f"Received a message event: {body}")
    # Extract the text from the message
    message_text = body.get("event", {}).get("text", "")
    logger.info(f"Message text: {message_text}")

    # Check if the message contains "create event" (case-insensitive)
    if re.search("create event", message_text, re.IGNORECASE):
        logger.info("'create event' detected in the message")
        # Call the create_event function directly
        create_event(body, logger)

def create_event(body, logger):
    logger.info("Creating event...")
    event = body.get("event", {})
    user = event.get("user")
    channel = event.get("channel")

    try:
        # Use client from the app object
        app.client.chat_postMessage(
            channel=channel,
            text=f"Hey <@{user}>! Let's create an event. Click the button to start.",
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn",
                             "text": f"Hey <@{user}>! Let's create an event. Click the button to start."},
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Create Event!"},
                        "action_id": "create_event_button"
                    }
                }
            ]
        )
        logger.info("Create event message sent successfully")
    except Exception as e:
        logger.error(f"Error sending create event message: {e}")

@app.action("create_event_button")
def open_create_event_modal(ack, body, client, logger):
    ack()
    logger.info(f"Button clicked. Body: {body}")
    channel_id = body.get("channel", {}).get("id") or body.get("container", {}).get("channel_id")
    if not channel_id:
        logger.error("Failed to get channel ID from body")
        return
    logger.info(f"Opening modal for channel: {channel_id}")
    try:
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "event_creation_modal",
                "title": {"type": "plain_text", "text": "Create Event"},
                "submit": {"type": "plain_text", "text": "Create"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "event_name",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "event_name_input"
                        },
                        "label": {"type": "plain_text", "text": "Name:"}
                    },
                    {
                        "type": "input",
                        "block_id": "event_date",
                        "element": {
                            "type": "datepicker",
                            "action_id": "event_date_input"
                        },
                        "label": {"type": "plain_text", "text": "Date:"}
                    },
                    {
                        "type": "input",
                        "block_id": "event_location",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "event_location_input"
                        },
                        "label": {"type": "plain_text", "text": "Location:"}
                    },
                    {
                        "type": "input",
                        "block_id": "event_description",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "event_description_input",
                            "multiline": True
                        },
                        "label": {"type": "plain_text", "text": "Description:"}
                    },
                    {
                        "type": "input",
                        "block_id": "event_start_time",
                        "element": {
                            "type": "timepicker",
                            "initial_time": "12:00",
                            "action_id": "event_start_time_input"
                        },
                        "label": {"type": "plain_text", "text": "Start Time:"}
                    },
                    {
                        "type": "input",
                        "block_id": "event_end_time",
                        "element": {
                            "type": "timepicker",
                            "initial_time": "13:00",
                            "action_id": "event_end_time_input"
                        },
                        "label": {"type": "plain_text", "text": "End Time:"}
                    }
                ],
                "private_metadata": channel_id
            }
        )
        logger.info("Modal opened successfully")
    except Exception as e:
        logger.error(f"Error opening modal: {e}")

@app.view("event_creation_modal")
def handle_event_creation_submission(ack, body, client, view, logger):
    ack()
    event_name = view["state"]["values"]["event_name"]["event_name_input"]["value"]
    event_date = view["state"]["values"]["event_date"]["event_date_input"]["selected_date"]
    event_location = view["state"]["values"]["event_location"]["event_location_input"]["value"]
    event_description = view["state"]["values"]["event_description"]["event_description_input"]["value"]
    event_start_time = view["state"]["values"]["event_start_time"]["event_start_time_input"]["selected_time"]
    event_end_time = view["state"]["values"]["event_end_time"]["event_end_time_input"]["selected_time"]

    logger.info(f"New event created: {event_name} on {event_date}")
    logger.info(f"Description: {event_description}")
    logger.info(f"Location: {event_location}")
    logger.info(f"Time: {event_start_time} - {event_end_time}")

    channel_id = view.get("private_metadata")
    if not channel_id:
        logger.error("No channel ID found in private_metadata")
        return

    logger.info(f"Attempting to send message to channel: {channel_id}")

    try:
        # Call the create_event function from the Google Calendar code
        create_google_calendar_event(event_name, event_date, event_location, event_description, event_start_time, event_end_time)

        result = client.chat_postMessage(
            channel=channel_id,
            text=f"A new event '{event_name}' has been created by <@{body['user']['id']}>!\n"
                 f"Date: {event_date}\n"
                 f"Time: {event_start_time} - {event_end_time}\n"
                 f"Location: {event_location}\n"
                 f"Description: {event_description}"
        )
        logger.info(f"Message sent successfully. Result: {result}")
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        try:
            client.chat_postMessage(
                channel=body['user']['id'],
                text=f"There was an error posting your event to the channel. Here are the details:\n"
                     f"Event: {event_name}\n"
                     f"Date: {event_date}\n"
                     f"Time: {event_start_time} - {event_end_time}\n"
                     f"Location: {event_location}\n"
                     f"Description: {event_description}"
            )
        except Exception as dm_error:
            logger.error(f"Error sending DM to user: {dm_error}")

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()