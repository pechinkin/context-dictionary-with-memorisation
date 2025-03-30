Here will be described, how program works.
#### 1. Initialization
We transfer all the words and sentences to `elasticsearch` (we use it for fast search). Also, we will have field/table with amount of times the word was met in user's experience.

#### 2. Searching a word
When a user searches a word, `elasticsearch` returns word's definition and sentences where the word is used.

#### 3. Relevance
Sentences are sorted by their familiarity to user. Every time user searches the word, we increase a counter of times, the word was met. The `delta` of increasing depends on several things:
- is it a word we are searching or we just meet in in given sentences
- how important and independent the part of speach is (prepositions, articles are less valuable here than verbs or nouns)

Basically, that's all