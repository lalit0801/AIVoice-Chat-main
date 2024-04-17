# from openai import OpenAI
# client = OpenAI(api_key="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")

# #create non stream model
# response = client



# response = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     {"role": "system", "content": "You are a indian guide only communicate related to india"},
#     {"role": "user", "content": "Who won the world series in 2020?"},
#     {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
#     {"role": "user", "content": "Where was it played?"}
#   ]
# )
# print(response)