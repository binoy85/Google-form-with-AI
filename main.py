from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
import json


SCOPES = "https://www.googleapis.com/auth/forms.body"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"
def createForm():
    store = file.Storage("token.json")
    creds = None
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets("E:\My Codes\python\Google_form\client_secrets.json", SCOPES)
        creds = tools.run_flow(flow, store)

    form_service = discovery.build(
        "forms",
        "v1",
        http=creds.authorize(Http()),
        discoveryServiceUrl=DISCOVERY_DOC,
        static_discovery=False,
    )

    with open('user_data.json', 'r') as f:
        data = json.load(f)
            # Request body for creating a form
        NEW_FORM = {
            "info": {
                "documentTitle": data["doc_title"],
                "title": data["form_title"]
                }
            }
            
    # Creates the initial form
    result = form_service.forms().create(body=NEW_FORM).execute()
    

    # Add description
    with open('user_data.json', 'r') as f:
        data = json.load(f)
        user_description = data["form_description"]

    # Request body to add description and update quiz settings to a Form
    update = {
        "requests": [
            {
                "updateFormInfo": {
                    "info": {
                        "description": user_description,
                    },
                    "updateMask": "description",
                }
            },
            {
            "updateSettings":{
                "settings":{
                "quizSettings":{
                    "isQuiz": True,
                }
                },
                "updateMask":"quizSettings",
            }
    },
        ]
    }

    # Update the form description and quiz settings
    form_service.forms().batchUpdate(formId= result["formId"], body=update).execute()

    # Function for request body to add a multiple-choice question
    def add_question(question, option1, option2, option3, option4, answer, marks, index = 0):
        NEW_QUESTION = {
            "requests": [
                {   
                    "createItem": {
                        "item": {
                            "title": (
                                question
                            ),
                            "questionItem": {
                                "question": {
                                    "required": True,
                                        "grading": {
                                            "pointValue": marks,
                                            "correctAnswers": {
                                            "answers": [{"value": answer}]
                                                },
                        "whenRight": {"text": "You got it!"},
                        "whenWrong": {"text": "Sorry, that's wrong"}
                                },
                                    "choiceQuestion": {
                                        "type": "RADIO",
                                        "options": [
                                            {"value": option1},
                                            {"value": option2},
                                            {"value": option3},
                                            {"value": option4},
                                        ],
                                        "shuffle": True,
                                    },
                                }
                            },
                        },
                        "location": {"index": index},
                    }
                }
            ]
        }

        # Adds the question to the form
        question_setting = (
            form_service.forms()
            .batchUpdate(formId=result["formId"], body=NEW_QUESTION)
            .execute()
        )

    with open('selected_questions.json', 'r') as f1, open('user_data.json', 'r') as f2:
        question_data = json.load(f1)

        # The api doesn't support '\n'
        for i in question_data:
            for j in i:
                i[j] = i[j].replace("\n", " ")

        user_data = json.load(f2)
        for i in question_data:
            try:
                add_question(question= i["question"], option1= i["Option1"], option2= i["Option2"], option3= i["Option3"], option4=i["Option4"],answer= i["answer"],marks= user_data["marks"], index= question_data.index(i))
            except:
                try:
                    add_question(question= i["question"], option1= i["Option1"], option2= i["Option2"], option3= i["Option3"], option4=i["Option4"],answer= i[i["answer"]],marks= user_data["marks"], index= question_data.index(i))
                except:
                    continue
    return result["formId"]
