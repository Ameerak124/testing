# importing libraries
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

class summarizzing:
	
	# def __init__(self,text):
	# 	self.text = text
	# Input text - to summarize
	#text = "International Business Machines Corporation is an American multinational technology corporation headquartered in Armonk, New York, with operations in over 171 countries. The company began in 1911, founded in Endicott, New York by trust businessman Charles Ranlett Flint, as the Computing-Tabulating-Recording Company and was renamed International Business Machines in 1924. IBM is incorporated in New York."

	def summarizer(self,text):
		# Tokenizing the text
		stopWords = set(stopwords.words("english"))
		words = word_tokenize(text)

		# Creating a frequency table to keep the
		# score of each word

		freqTable = dict()
		for word in words:
			word = word.lower()
			if word in stopWords:
				continue
			if word in freqTable:
				freqTable[word] += 1
			else:
				freqTable[word] = 1

		# Creating a dictionary to keep the score
		# of each sentence
		sentences = sent_tokenize(text)
		sentenceValue = dict()

		for sentence in sentences:
			for word, freq in freqTable.items():
				if word in sentence.lower():
					if sentence in sentenceValue:
						sentenceValue[sentence] += freq
					else:
						sentenceValue[sentence] = freq



		sumValues = 0
		for sentence in sentenceValue:
			sumValues += sentenceValue[sentence]
			

		# Average value of a sentence from the original text

		average = int(sumValues / len(sentenceValue))


		# Storing sentences into our summary.
		summary = ''

		for sentence in sentences:
			
			if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.2 * average)):
				
				summary += " " + sentence
				
		return(summary)

# #text = "International Business Machines Corporation is an American multinational technology corporation headquartered in Armonk, New York, with operations in over 171 countries. The company began in 1911, founded in Endicott, New York by trust businessman Charles Ranlett Flint, as the Computing-Tabulating-Recording Company and was renamed International Business Machines in 1924. IBM is incorporated in New York."
# test = summarizzing()
# print(test.summarizer(text))

