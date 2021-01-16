key = "66809a9c3def40138dcf988dd9b13db5"
endpoint = "https://textkeywords.cognitiveservices.azure.com/"

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential


def authenticate_client():
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint, credential=ta_credential)
    return text_analytics_client


client = authenticate_client()

def sentiment_analysis(client, meeting_content):
    out = ""
    response = client.analyze_sentiment(documents = meeting_content)[0]
    out += "Meeting Sentiment: {}".format(response.sentiment)
    out += "\n\tOverall scores: positive={0:.2f}; neutral={1:.2f}; negative={2:.2f} \n".format(
        response.confidence_scores.positive,
        response.confidence_scores.neutral,
        response.confidence_scores.negative,
    )
    return out


yay = sentiment_analysis(client, ["i'm so happy"])
print(yay)

rip = sentiment_analysis(client, ["i hate my life"])
print(rip)