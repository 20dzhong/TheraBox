import re

string = "I'm sorry to hear that things aren't going so well in your life. It sounds like you may be feeling a little bit lonely and isolated.  Did you always feel this way? What do you think might have caused you to feel this way?"

# check if incomplete sentences
for i in range(len(string), 0, -1):

    if string[i - 1:i] != "." and string[i - 1:i] != "?" and string[i - 1:i] != "!":
        string = string[0:i]
    else:
        break

a = re.sub('[^a-zA-Z.,?\'\d\s]', ' ', string)
print(a)
