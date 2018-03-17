from config import *
from database import get_db_session
from textpreprocessor import TextPreProcessor
from models.traincache import TrainCache
from models.features import Features
from sqlalchemy.dialects import mysql
from collections import defaultdict
from sqlalchemy import func
import decimal
import math
import sys


class SentimentAnalyser:

    def __init__(self):
        self.session = get_db_session()
        self.text_pre_processor = TextPreProcessor()
        self.train_total = {0: 0, 1: 0, 2: 0, "total": 0}

        query = self.session.query(TrainCache)
        for row in query.all():
            self.train_total["total"] += row.qty
            self.train_total[row.sentiment] = row.qty

        self.total_vocab_size = self.session.query(Features).count()

        self.features_total = {0: 0, 1: 0, 2: 0}
        query = self.session.query(
            Features.sentiment,
            func.sum(Features.count).label("total")
        ).group_by(Features.sentiment)
        for row in query.all():
            self.features_total[row.sentiment] = row.total

    def neutral_match(self, features):
        if len(features) < 3:
            return 1
        for feature in features:
            if feature == "dm" or feature == "sent":
                return 1
        return 0

    def multinomial_naive_bayes(self, text):
        processed_text = self.text_pre_processor.process_text(text)

        features = self.text_pre_processor.remove_stemmed_stop_words(
            self.text_pre_processor.generate_features(processed_text)
        )

        if self.neutral_match(features):
            return {0: 0, 1: 1, 2: 0}

        feature_scores = self.get_features_scores(features)

        score = {0: 0, 1: 0, 2: 0}

        decimal.getcontext().rounding = decimal.ROUND_DOWN
        decimal.getcontext().prec = 200

        score[0] = math.log(
            decimal.Decimal(self.train_total[0]) /
            decimal.Decimal(self.train_total["total"])
        )
        score[1] = math.log(
            decimal.Decimal(self.train_total[1]) /
            decimal.Decimal(self.train_total["total"])
        )
        score[2] = math.log(
            decimal.Decimal(self.train_total[2]) /
            decimal.Decimal(self.train_total["total"])
        )

        for feature in features:
            top = {0: 0, 1: 0, 2: 0}
            bottom = {0: 0, 1: 0, 2: 0}

            if feature in feature_scores and 0 in feature_scores[feature]:
                top[0] = feature_scores[feature][0]
                feature_scores[feature][0]
            if feature in feature_scores and 1 in feature_scores[feature]:
                top[1] = feature_scores[feature][1]
            if feature in feature_scores and 2 in feature_scores[feature]:
                top[2] = feature_scores[feature][2]

            # Increment each by one to prevent division by zero errors
            top[0] += 1
            top[1] += 1
            top[2] += 1

            bottom[0] = self.features_total[0] + self.total_vocab_size
            bottom[1] = self.features_total[1] + self.total_vocab_size
            bottom[2] = self.features_total[2] + self.total_vocab_size

            score[0] += math.log(
                decimal.Decimal(top[0]) / decimal.Decimal(bottom[0])
            )
            score[1] += math.log(
                decimal.Decimal(top[1]) / decimal.Decimal(bottom[1])
            )
            score[2] += math.log(
                decimal.Decimal(top[2]) / decimal.Decimal(bottom[2])
            )

        if score[0] > score[1] and score[0] > score[2]:
            return 0
        elif score[1] > score[0] and score[1] > score[2]:
            return 1
        elif score[2] > score[0] and score[2] > score[1]:
            return 2
        else:
            return -1

    def get_features_scores(self, features):
        query = self.session.query(Features).\
            filter(Features.feature.in_(features))

        feature_scores = defaultdict(dict)
        for row in query.all():
            feature_scores[row.feature][row.sentiment] = row.count

        return feature_scores

if __name__ == '__main__':
    SA = SentimentAnalyser()
    print SA.multinomial_naive_bayes(sys.argv[1])
