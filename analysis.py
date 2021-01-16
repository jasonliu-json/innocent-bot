
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from bot_token import key
from bot_token import endpoint
def authenticate_client():
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint, credential=ta_credential)
    return text_analytics_client


client = authenticate_client()

def sentiment_analysis(client, content):
    out = ""
    response = client.analyze_sentiment(documents = [content])[0]
    out += "Sentiment: {}".format(response.sentiment)
    out += "\n\tOverall scores: positive={0:.2f}; neutral={1:.2f}; negative={2:.2f} \n".format(
        response.confidence_scores.positive,
        response.confidence_scores.neutral,
        response.confidence_scores.negative,
    )
    return out

if __name__ == "__main__":
    while True:
        print(sentiment_analysis(client, input("type something here to evalute sentiment: ")))

# yay = sentiment_analysis(client, ["i'm so happy"])
# print(yay)
#
# rip = sentiment_analysis(client, ["i hate my life"])
# print(rip)