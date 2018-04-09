import re
from nltk.stem import PorterStemmer


class TextPreProcessor(object):

    def process_text(self, textstring):
        # Convert Text String To Lower
        textstring = textstring.lower()

        # Remove any URLs
        textstring = re.sub(r"http\S+", "", textstring)

        # Remove all non alpha, space and # characters
        textstring = re.sub(r'[^a-z\s#]', '', textstring)

        # Remove any repeating characters
        textstring = re.sub(r'([a-z])\1+', r'\1', textstring)

        # Remove all words starting with @ and split in to an array
        textstring_list = filter(lambda x: x[0] != '@', textstring.split())

        stemmer = PorterStemmer()
        try:
            xrange
        except NameError:
            xrange = range
        for i in xrange(len(textstring_list)):
            # Convert abreviations
            textstring_list[i] = self.convert_abbreviations(textstring_list[i])

            # Stem any words
            textstring_list[i] = stemmer.stem(textstring_list[i])

        return textstring_list

    def generate_features(self, list_of_words):
        previous_word = ""
        return_list = []

        while len(list_of_words) > 0:
            if len(previous_word) > 0:
                new_feature = previous_word + " " + list_of_words[0]
                return_list.append(new_feature)
            return_list.append(list_of_words[0])
            previous_word = list_of_words.pop(0)

        return return_list

    def remove_stop_words(self, list_of_words):
        # Build our stop words dict
        stopwords = set()
        fh = open('stopwords.txt', 'r')
        for line in fh.readlines():
            stopwords.add(line.strip('\n'))
        fh.close()

        list_of_words = [x for x in list_of_words if x not in stopwords]
        return list_of_words

    def remove_stemmed_stop_words(self, list_of_words):
        # Build our stop words dict
        stopwords = set()
        fh = open('intweet/stemmed_stop_words.txt', 'r')
        for line in fh.readlines():
            stopwords.add(line.strip('\n'))
        fh.close()

        list_of_words = [x for x in list_of_words if x not in stopwords]
        return list_of_words

    def stem_my_stop_words(self):
        fh1 = open('intweet/stopwords.txt', 'r')
        fh2 = open('intweet/stemmed_stop_words.txt', 'w')
        stemmer = PorterStemmer()
        for line in fh1.readlines():
            fh2.write(stemmer.stem(line.strip('\n')) + "\n")
        fh1.close()
        fh2.close()

    def convert_abbreviations(self, textstring):
        abbreviation_dict = {
            'fml': 'fuck my life',
            'lol': 'lol',
            'lmao': 'lol',
            'rofl': 'lol',
            'can\'t': 'cannot',
            'hasn\'t': 'has not',
            'hasnt': 'has not',
            'didn\'': 'did not',
            'couldn\'t': 'could not',
            'shouldn\'': 'should not',
            'couldnt': 'could not',
            'shouldnt': 'should not',
            'wouldn\'t': 'would not',
            'wouldnt': 'would not',
            'aint': 'is not',
            'ain\'t': 'is not',
            'isn\'t': 'is not',
            'isnt': 'is not',
            'pls': 'please',
        }
        if textstring in abbreviation_dict:
            return abbreviation_dict[textstring]
        else:
            return textstring


if __name__ == '__main__':
    text = "Thiiis iiis aaaa.   - where rather lmao #word 12tweet \
        shopping @leon yes I am really happy! http://www.google.com \
        https://someurl.co.uk"

    tpp = TextPreProcessor()
    tpp.stem_my_stop_words()
    processed_text = tpp.process_text(text)
    list_of_features = tpp.remove_stemmed_stop_words(
        tpp.generate_features(processed_text)
    )
