from __future__ import print_function

import os.path
import pickle

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from utils import sendmessage, time

load_dotenv()


class GmailAPI:
    def __init__(self):
        # If modifying these scopes, delete the file token.json.
        self._SCOPES = [
            "https://www.googleapis.com/auth/gmail.compose",
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.labels",
            "https://www.googleapis.com/auth/gmail.modify",
        ]

    def ConnectGmail(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # flow = InstalledAppFlow.from_client_secrets_file(
                #     "credentials.json", self._SCOPES
                # )
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"), self._SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

        service = build("gmail", "v1", credentials=creds)

        return service

    def ModifyMessage(self, messageId):

        service = self.ConnectGmail()

        labels_mod = {
            "ids": messageId,
            "removeLabelIds": ["UNREAD"],
            "addLabelIds": [],
        }

        service.users().messages().batchModify(userId="me", body=labels_mod).execute()

    def GetMessageList(self, DateFrom, DateTo, MessageFrom):

        # Connect to Gmailapi
        service = self.ConnectGmail()

        MessageList = []

        query = ""
        # Specify query
        if DateFrom != None and DateFrom != "":
            query += "after:" + DateFrom + " "
        if DateTo != None and DateTo != "":
            query += "before:" + DateTo + " "
        if MessageFrom != None and MessageFrom != "":
            query += "From:" + MessageFrom + " "

        # Get unread gmail list with userID="me" and query
        messageIDlist = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["UNREAD"], q=query)
            .execute()
        )

        if messageIDlist["resultSizeEstimate"] == 0:
            print("Message is not found")
            return MessageList

        # Get gmail detail (date, from, subject and snippet)
        for message in messageIDlist["messages"]:
            row = {}
            row["ID"] = message["id"]
            MessageDetail = (
                service.users().messages().get(userId="me", id=message["id"]).execute()
            )
            for header in MessageDetail["payload"]["headers"]:
                if header["name"] == "Date":
                    row["Date"] = time.format_string_date(header["value"])
                elif header["name"] == "From":
                    row["From"] = header["value"]
                elif header["name"] == "Subject":
                    row["Subject"] = header["value"]

            row["Content"] = MessageDetail["snippet"]
            MessageList.append(row)

            self.ModifyMessage(message["id"])
        return MessageList


def main():
    app = GmailAPI()
    messages = app.GetMessageList(
        DateFrom=time.fetch_today(),
        DateTo=None,
        MessageFrom=os.environ.get("MESSAGE_FROM"),
    )

    for message in messages:
        content = ""
        content += message["From"] + "\n\n"
        content += message["Date"] + "\n\n"
        content += message["Subject"] + "\n\n"
        content += message["Content"]

        sendmessage.push_message(content)


if __name__ == "__main__":
    main()
