from flask import Flask, request, jsonify
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext, MessageFactory
from botbuilder.schema import Activity
import asyncio
import requests

app = Flask(__name__)

# Replace with your Azure Bot credentials
APP_ID = "f33b568d-7df4-4506-99d7-c1e6181d89a6" # Replace with actual App ID
APP_PASSWORD = "6d6bc088-0f89-4d91-a668-c66cf55f5da5" # Replace with actual App Password
adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

# LINE API endpoint and credentials
LINE_API_URL = "https://api.line.me/v2/bot/message/reply"
# Replace with actual Channel Access Token
LINE_CHANNEL_ACCESS_TOKEN = "ybp773K45do/RrbmJh5qllNDY1e4mS/pAulAxT0WHIKhhQhgMx0ZHLZBnCdnAz1PETXV/RMiqG5zayWlDVSmVPtzVyXRCXLkY+XXhNvKQxRowheGs1fxmEPDw5cRQqEiPJkQu/8KpJeQVxlXcAKE5QdB04t89/1O/w1cDnyilFU="

# Handle incoming messages from LINE
@app.route("/line/webhook", methods=["POST"])
def line_webhook():
    data = request.json
    for event in data["events"]:
        if event["type"] == "message":
            user_message = event["message"]["text"]
            user_id = event["source"]["userId"]

            # Create an activity for Azure Bot Service
            activity = Activity(
                type="message",
                text=user_message,
                from_property={"id": user_id},
                channel_id="line"
            )

            # Process the activity with Azure Bot Service
            async def process_activity():
                await adapter.process_activity(activity, lambda context: on_message(context))
            asyncio.run(process_activity())

    return jsonify({"status": "ok"})

# Handle messages from Azure Bot Service
async def on_message(context: TurnContext):
    response_text = f"You said: {context.activity.text}"
    await context.send_activity(MessageFactory.text(response_text))

    # Send the response back to LINE
    reply_to_line(context.activity.from_property.id, response_text)

# Send a reply to LINE
def reply_to_line(user_id, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": "dummy_reply_token",  # Replace with actual reply token if needed
        "messages": [{"type": "text", "text": text}]
    }
    requests.post(LINE_API_URL, headers=headers, json=payload)

# Start the server
if __name__ == "__main__":
    app.run(port=3978)