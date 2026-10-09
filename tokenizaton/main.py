import re
text = ""

with open('./constant.txt', 'r', encoding='utf-8') as file:
    text = file.read()


result = re.split(r'([,.:;?_!"()\']|--|\s)', text)
result = [x.strip() for x in result if x.strip()]

mySetResult = sorted(set(result))
mySetResult.append("<|endoftext|>")
mySetResult.append("<|unk|>")

word_to_position_encoding = {word: i + 1 for i, word in enumerate(mySetResult)}
word_to_position_decoding = {i + 1: word for i, word in enumerate(mySetResult)}


def convertTextToToken(text: str):
    textArray = re.split(r'([,.:;?_!"()\'\']|--|\s)', text)
    result = [x.strip() for x in textArray if x.strip()]
    encodedText = []
    for word in result:
        if word in word_to_position_encoding:
            encodedText.append(word_to_position_encoding[word])
        else:
            encodedText.append(word_to_position_encoding["<|unk|>"])
    return encodedText

def convertTokenToText(token: list):
    textArray = []
    for word in token:
        textArray.append(word_to_position_decoding[word])
    return " ".join(textArray)
    
print(convertTextToToken("the requirement .dghgjhgdhgjdfgjhgdfgjghj,"))
print(convertTokenToText([10919, 12110, 18, 12110, 14]))