from config import *
from database import get_db_session
from textpreprocessor import TextPreProcessor
from models.traincache import TrainCache
from models.features import Features
from sqlalchemy.dialects import mysql
from collections import defaultdict
import decimal
import sys

class SentimentAnalyser:
    
    def __init__(self, dbsession):
        self.session = dbsession
        self.total = { 0:0 , 1:0, 2:0 }
        query = self.session.query(TrainCache)
        for row in query.all():
            self.total[row.sentiment] = row.qty
            
        self.total_vocab_size = self.session.query(Features).count()
            
    def neutral_match(self, features):
        if len(features) < 3:
            return 1
        for feature in features:
            if feature == "dm" or feature == "sent":
                return 1
        return 0

    def multinomial_naive_bayes(self, text):
        tpp = TextPreProcessor()
        processed_text = tpp.process_text(text)

        features = tpp.remove_stemmed_stop_words(tpp.generate_features(processed_text))

        if self.neutral_match(features):
            return { 0:0, 1:1, 2:0 }
        
        feature_scores = self.get_features_scores(features)
        
        top = { 0:0, 1:0, 2:0 }
        bottom = { 0:0, 1:0, 2:0 }
        score = { 0:0, 1:0, 2:0 }
        
        decimal.getcontext().rounding = decimal.ROUND_DOWN
        decimal.getcontext().prec = 200
        
        for feature in features:
            if feature in feature_scores and 0 in feature_scores[feature]:
                top[0] = feature_scores[feature][0]
            
            if feature in feature_scores and 1 in feature_scores[feature]:
                top[1] = feature_scores[feature][1]
                
            if feature in feature_scores and 2 in feature_scores[feature]:
                top[2] = feature_scores[feature][2]
                
            # Increment by one to each to prevent division by zero errors
            top[0] += 1
            top[0] += 1
            top[0] += 1

            bottom[0] = self.total[0] + self.total_vocab_size
            bottom[1] = self.total[1] + self.total_vocab_size
            bottom[2] = self.total[2] + self.total_vocab_size
            
            score[0] += decimal.Decimal(top[0]) / decimal.Decimal(bottom[0])
            score[1] += decimal.Decimal(top[1]) / decimal.Decimal(bottom[1])
            score[2] += decimal.Decimal(top[2]) / decimal.Decimal(bottom[2])

        if score[0] > score[1] and score[0] > score[2]:
            return "Negative"
        
        if score[1] > score[0] and score[1] > score[2]:
            return "Neutral"
            
        if score[2] > score[0] and score[2] > score[1]:
            return "Positive"                

    def get_features_scores(self, features):
        query = self.session.query(Features).\
            filter(Features.feature.in_(features))

        feature_scores = defaultdict(dict)
        for row in query.all():
            feature_scores[row.feature][row.sentiment] = row.count
            
        return feature_scores
        
if __name__ == '__main__':
    session = get_db_session()
    SA = SentimentAnalyser(session)

    print SA.multinomial_naive_bayes(sys.argv[1])