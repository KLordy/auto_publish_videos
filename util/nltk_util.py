import nltk
from nltk.tokenize import sent_tokenize

# 下载NLTK的punkt分词器（如果尚未下载）
nltk.download('punkt')

# 文章示例
article = """
The way this polar bear walks is a bit casual because it knows the physics of walking on ice.
"""
# article = """
# Natural Language Processing (NLP) is a field of artificial intelligence
# that focuses on the interaction between computers and humans through
# natural language. NLP techniques are used to analyze, understand, and
# derive meaning from human language in a smart and useful way.
#
# NLTK is a leading platform for building Python programs to work with
# human language data. It provides easy-to-use interfaces to over 50
# corpora and lexical resources, such as WordNet, along with a suite
# of text processing libraries for classification, tokenization,
# stemming, tagging, parsing, and semantic reasoning.
#
# Using NLTK, we can easily tokenize sentences from a given article.
# """

# 对文章进行断句
sentences = sent_tokenize(article)

# 打印断句结果
for i, sentence in enumerate(sentences, 1):
    print(f"Sentence {i}: {sentence.strip()}\n\n")
    print('\n')
