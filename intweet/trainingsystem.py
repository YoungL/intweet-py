from intweet.database import get_db_session
from intweet.models.tweet import Tweet
from intweet.textpreprocessor import TextPreProcessor
from sqlalchemy.orm.exc import NoResultFound
from collections import Counter
import re


class TrainingSystem:

    def train_on_tweet(self, tweet_id, sentiment):

        # Understand the previous sentiment
        db = get_db_session()
        query = db.query(Tweet).filter(Tweet.id == tweet_id)

        try:
            tweet = query.one()
        except NoResultFound:
            raise ValueError("Invalid tweet_id")

        if sentiment not in (0, 1, 2):
            raise ValueError("Expected sentiment to be 0, 1 or 2")

        # Don't train on the same tweet more than once!
        if tweet.trained > 0:
            return True

        # Step 1. Update the sentiment on the tweet
        tweet.trained = 1
        tweet.sentiment = sentiment
        db.commit()

        # Step 2. Train the system
        return self.train({sentiment: [tweet.tweet]})

    '''
    This function expects:
    list_of_sorted_tweets = {
        0: [List, Of, Pieces, Of, Text]
        1: [List, Of, Pieces, Of, Text]
        2: [List, Of, Pieces, Of, Text]
    }
    '''
    def train(self, list_of_sorted_texts):

        tpp = TextPreProcessor()
        db = get_db_session()
        feature_histogram = {0: Counter(), 1: Counter(), 2: Counter()}
        training_count_data = []
        training_text_items = []

        for sentiment, list_of_text in list_of_sorted_texts.iteritems():

            # Keeping a list of number of training texts per sentiment
            training_count_data.append(
                "(%d, %d)" % (sentiment, len(list_of_text))
            )

            for text in list_of_text:

                # Keep record of each piece of text used to train system
                training_text_items.append(
                    "('%s', %d)" % (re.escape(text), sentiment)

                )

                processed_text = tpp.process_text(text)
                list_of_features = tpp.remove_stemmed_stop_words(
                    tpp.generate_features(processed_text)
                )
                for feature in list_of_features:
                    feature_histogram[sentiment][feature] += 1

        features_data = []
        for sentiment, features in feature_histogram.iteritems():
            for feature, count in features.iteritems():
                features_data.append(
                    "('%s', %d, %d)" % (feature, sentiment, count)
                )

        # Commit the training to the database
        query = "INSERT INTO tbl_train_data (raw_tweet,sentiment) VALUES %s "\
            % (",".join(training_text_items))

        db.execute(query)
        db.commit()

        query = "INSERT INTO tbl_train_count_live (sentiment, qty) VALUES %s \
            ON DUPLICATE KEY UPDATE qty=qty + values(qty)" \
            % (",".join(training_count_data))

        db.execute(query)
        db.commit()

        query = "INSERT INTO tbl_features_live (feature, sentiment, count) \
            VALUES %s ON DUPLICATE KEY UPDATE count=count+values(count)" \
            % (",".join(features_data))

        db.execute(query)
        db.commit()

        return True
