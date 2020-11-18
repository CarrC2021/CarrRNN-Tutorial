import numpy as np
text_data = open("ptb.train.txt", 'r', encoding='utf-8').read()
text_data = text_data.lower()
vocabulary = dict()
count = 0
parsed_text = text_data.split(' ')
for i in range(len(parsed_text)):
    if parsed_text[i] not in vocabulary:
        vocabulary.update({parsed_text[i]: count})
        count += 1
print(vocabulary)


text_data = open("ptb.train.txt", 'r', encoding='utf-8').read()
text_data = text_data.lower()
parsed_text = np.array(text_data.split(' '))
for i in range(len(parsed_text)):
    if parsed_text[i] in vocabulary:
        parsed_text[i] = vocabulary.get(parsed_text[i])

print(parsed_text[:700])

