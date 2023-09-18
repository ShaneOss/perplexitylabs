# perplexitylabs
A python api to use labs.perplexity.ai using Selenium.

# Rquirements:
pip install fake-useragent
pip install beautifulsoup4
pip install selenium
pip install selenium-wire

# Usage
You can import the Perplexity class and use it like this:
```python
from Perplexity_Selenium import Perplexity

perplexity = Perplexity()
answer = perplexity.search("What is the meaning of life?")
print(answer)
```
# The model used can be updated in Perplexity.py
    #Available Models
    # codellama-34b-instruct
    # llama-2-7b-chat
    # llama-2-13b-chat
    # llama-2-70b-chat
    self.model = "llama-2-70b-chat"

You can even create a cli tool with it:
```python
from Perplexity import Perplexity

perplexity = Perplexity()

while True:
    inp = str(input("> "))
    c = perplexity.search(inp)
    if c:
        print(c)
```
