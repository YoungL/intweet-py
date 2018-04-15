from intweet.models.user import User
from intweet.models.rule import Rule
from intweet.models.tweet import Tweet
from intweet.sentiment_analyser import SentimentAnalyser
from intweet.config import CONFIG
from flask import render_template, request, url_for,\
    session, redirect, Blueprint
from intweet.database import get_db_session
import validators
import re
from sqlalchemy import func, and_
from sqlalchemy.orm.exc import NoResultFound
import datetime
from collections import OrderedDict
from intweet.trainingsystem import TrainingSystem


bp = Blueprint('routes', __name__)


@bp.route('/')
@bp.route('/dashboard')
@bp.route('/home')
def home():
    local_config = {
        "page_name": "Home",
        "home": True,
        "dashboard": True
    }
    # Home Page
    if session.get('logged_in'):
        userdata = {
            'fullname': session.get('name'),
            'email': session.get('email')
        }
        return render_template(
            'user_home.html',
            global_config=CONFIG,
            local_config=local_config,
            menu_rules=generate_menu_items(),
            userdata=userdata
        )
    else:
        return render_template(
            'home.html',
            global_config=CONFIG,
            local_config=local_config
        )


@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('email', None)
    session.pop('name', None)
    return redirect(url_for('routes.home'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Login Page
    error = {}
    error['errors'] = 0
    if request.method == 'POST':
        if not request.form['email'] or len(request.form['email']) == 0:
            error['message'] = "No email address provided"
            error['errors'] += 1

        elif not request.form['password'] or \
                len(request.form['password']) == 0:
            error['message'] = "No password provided"
            error['errors'] += 1

        else:
            # Attempt to log the user in
            db = get_db_session()
            query = db.query(User).\
                filter(User.email == request.form['email'])
            user = query.one()
            if not user.validate_password(request.form['password']):
                # email and password incorrect
                error['message'] = "Invalid credentials"
                error['errors'] += 1
            else:
                # email and password correct - log the user in!
                session['logged_in'] = True
                session['user'] = user.email
                session['name'] = user.fullname
                session['user_id'] = user.id
                return redirect(url_for('routes.home'))

    local_config = {
        "page_name": "Login"
    }
    return render_template('login.html', global_config=CONFIG,
                           local_config=local_config, error=error)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Register Page
    error = {}
    error['errors'] = 0
    db = get_db_session()

    if request.method == 'POST':
        if not request.form['email'] or len(request.form['email']) == 0:
            error['message'] = "No email address provided"
            error['errors'] += 1

        elif not request.form['password'] or \
                len(request.form['password']) == 0:
            error['message'] = "No password provided"
            error['errors'] += 1

        elif not request.form['fullname'] or \
                len(request.form['fullname']) == 0:
            error['message'] = "No full name provided"
            error['errors'] += 1

        elif not validators.email(request.form['email']):
            error['message'] = "Invalid email address provided"
            error['errors'] += 1

        elif len(request.form['password']) < 8 or \
                re.search('[0-9]', request.form['password']) is None or \
                re.search('[A-Z]', request.form['password']) is None or \
                re.search('[a-z]', request.form['password']) is None:
            error['message'] = "Password does not meet requirements"
            error['errors'] += 1

        elif db.query(User).filter(
                User.email == request.form['email']).count() > 0:
            error['message'] = "User already registered"
            error['errors'] += 1

        else:
            # We can actually register them now!
            user = User(
                fullname=request.form['fullname'],
                email=request.form['email'],
                password=request.form['password'],
                admin=0,
                active=1
            )
            db.add(user)
            db.commit()

            session['logged_in'] = True
            session['user'] = user.email
            session['name'] = user.fullname
            session['user_id'] = user.id
            return redirect(url_for('routes.home'))

    local_config = {
        "page_name": "Register"
    }

    return render_template(
        'register.html',
        global_config=CONFIG,
        local_config=local_config,
        error=error
    )


@bp.route('/prioritytweets/', methods=['GET'])
def prioritytweets_show():
    if not session.get('logged_in'):
        return redirect(url_for('routes.home'))
    else:
        userdata = {
            'fullname': session.get('name'),
            'email': session.get('email'),
            'user_id': session.get('user_id')
        }
        local_config = {
            "page_name": "Priority Tweets",
            "monitor": True,
            "prioritytweets": True
        }

        db = get_db_session()
        results = db.execute(
            'SELECT t1.rulename, t1.id, ( \
                SELECT count(*) \
                FROM tbl_raw_tweets t2 \
                WHERE t1.id = t2.rule \
                    AND t2.sentiment=0 \
                    AND timestamp > CURDATE()-2 \
            ) AS negative_count, (\
                SELECT count(*) \
                FROM tbl_raw_tweets t2 \
                WHERE t1.id = t2.rule \
                    AND t2.sentiment=1 \
                    AND timestamp > CURDATE()-2 \
            ) AS neutral_count,( \
                SELECT count(*) \
                FROM tbl_raw_tweets t2 \
                WHERE t1.id = t2.rule \
                    AND t2.sentiment=2 AND \
                    timestamp > CURDATE()-2 \
            ) AS positive_count \
            FROM tbl_monitor t1 \
            WHERE t1.userid=1 \
              AND t1.parentrule IS NULL \
            GROUP BY t1.id \
            ORDER BY t1.rulename ASC'
        )

        return render_template(
            'user_priority_tweets_table.html',
            global_config=CONFIG,
            local_config=local_config,
            userdata=userdata,
            menu_rules=generate_menu_items(),
            results_table=results
        )


@bp.route('/prioritytweets/<path:sentiment>/<path:rule>/<path:hours>')
def prioritytweets_show_rule(sentiment, rule, hours):
    if not session.get('logged_in'):
        return redirect(url_for('routes.home'))
    else:
        userdata = {
            'fullname': session.get('name'),
            'email': session.get('email'),
            'user_id': session.get('user_id')
        }

    # Validate our variable inputs
    if sentiment not in ("negative", "positive", "neutral"):
        return error_page("Invalid URL")

    try:
        rule = int(rule)
        hours = int(hours)
    except ValueError:
        return error_page("Invalid URL")

    db = get_db_session()
    query = db.query(Rule).\
        filter(and_(Rule.id == rule, Rule.userid == userdata['user_id']))

    try:
        rule = query.one()
    except NoResultFound:
        return error_page("Invalid Rule ID")

    local_config = {
        "page_name": "Priority Inbox for %s (%s)" % (rule.rulename, sentiment),
        "monitor": True,
        "prioritytweets": True
    }

    timefilter = datetime.date.today() - datetime.timedelta(hours=hours)

    query = db.query(Tweet).filter(
        Tweet.rule == rule, Tweet.timestamp > timefilter
    )

    prioritytweets = query.all()

    return render_template(
        'user_priority_tweets.html',
        global_config=CONFIG,
        local_config=local_config,
        userdata=userdata,
        ruledata=rule,
        sentiment=sentiment,
        tweets=prioritytweets,
        menu_rules=generate_menu_items()
    )


@bp.route('/train/feedback/<path:tid>/<path:sent>', methods=['GET', 'POST'])
def prioritytweets_retrain(tid, sent):
    if not session.get('logged_in'):
        return redirect(url_for('routes.home'))
    else:
        userdata = {
            'fullname': session.get('name'),
            'email': session.get('email'),
            'user_id': session.get('user_id')
        }

        try:
            tweet_id = int(tid)
            sentiment = int(sent)
        except ValueError:
            return error_page("Invalid URLs")

        # Check the tweet belongs to the user
        db = get_db_session()
        query = db.query(
            Tweet
        ).join(
            Rule
        ).filter(
            and_(Tweet.id == tweet_id, Rule.userid == userdata['user_id'])
        )

        try:
            query.one()
        except NoResultFound:
            return error_page("Invalid Tweet ID")

        ts = TrainingSystem()
        return error_page(ts.train_on_tweet(tweet_id, sentiment))


@bp.route('/analytics/show/<path:rule>', methods=['POST', 'GET'])
def analytics_show(rule):
    if not session.get('logged_in'):
        return redirect(url_for('routes.home'))
    else:
        userdata = {
            'fullname': session.get('name'),
            'email': session.get('email'),
            'user_id': session.get('user_id')
        }

        # Default finish and start times
        finish = datetime.date.today()
        start = finish - datetime.timedelta(days=7)

        # Override finish and start times if set
        if request.method == 'POST':
            if request.form['start']:
                start = datetime.datetime.strptime(
                    request.form['start'], '%d/%m/%Y'
                )
            if request.form['finish']:
                finish = datetime.datetime.strptime(
                    request.form['finish'], '%d/%m/%Y'
                )

        # This will validate that the rule belongs to the user and exists
        db = get_db_session()
        query = db.query(Rule).\
            filter(and_(Rule.id == rule, Rule.userid == userdata['user_id']))

        try:
            rule = query.one()
        except NoResultFound:
            return error_page("Invalid Rule ID")

        query = db.query(
            func.date(Tweet.timestamp).label('date'),
            Tweet.sentiment,
            func.count(Tweet.sentiment).label('qty')
        ).filter(
            Tweet.timestamp > start,
            Tweet.timestamp < finish,
            Tweet.rule == rule
        ).group_by(
            func.date(Tweet.timestamp),
            Tweet.sentiment
        ).order_by(
            func.date(Tweet.timestamp)
        )

        analyticdata = query.all()

        resultarray = OrderedDict()
        for result in analyticdata:
            if result.date not in resultarray:
                resultarray[result.date] = {}
            resultarray[result.date][result.sentiment] = int(result.qty)

        returnresult = OrderedDict()
        for result_date, sentiment_dict in resultarray.iteritems():
            returnresult[result_date] = {0: 0, 1: 0, 2: 0}
            tsum = count = 0
            for key, value in sentiment_dict.iteritems():
                tsum += int(value)
                count += 1

            for sentiment, value in sentiment_dict.iteritems():
                returnresult[result_date][sentiment] = (
                    float(value) / tsum
                ) * 100

        local_config = {
            "page_name": "Analytics for %s" % (rule.rulename),
            "analytics": True
        }

        return render_template(
            'user_analytics.html',
            global_config=CONFIG,
            local_config=local_config,
            userdata=userdata,
            start=start,
            finish=finish,
            ruledata=rule,
            menu_rules=generate_menu_items(),
            analyticdata=returnresult
        )


@bp.route('/monitor/rule/<path:rule>', methods=['POST'])
def monitor_rule_post(rule):
    if not session.get('logged_in'):
        return redirect(url_for('routes.home'))
    else:
        userdata = {
            'fullname': session.get('name'),
            'email': session.get('email'),
            'user_id': session.get('user_id')
        }
        local_config = {
            "page_name": "Add Monitoring Rule",
            "monitor": True,
            "viewrules": True
        }

        error = {"errors": 0, "message": ""}

        if not request.form['rulename']:
            error['errors'] += 1
            error['message'] = "Rulename is required"

        if not request.form['keywords']:
            error['errors'] += 1
            error['message'] = "Keywords are required"

        if not request.form['description']:
            error['errors'] += 1
            error['message'] = "Description is required"

        if not request.form['account_handle']:
            error['errors'] += 1
            error['message'] = "Twitter Handle is required"

        if not request.form['active']:
            error['errors'] += 1
            error['message'] = "Active is required"

        success = ""
        db = get_db_session()
        query = db.query(Rule).\
            filter(and_(Rule.id == rule, Rule.userid == userdata['user_id']))

        try:
            rule = query.one()
        except NoResultFound:
            return error_page("Invalid Rule ID")

        if error['errors'] == 0:
            if request.form['active'] == 'yes':
                active = 1
            else:
                active = 0
            rule.rulename = request.form['rulename']
            rule.keywords = request.form['keywords']
            rule.account_handle = request.form['account_handle']
            rule.description = request.form['description']
            rule.active = active
            db.commit()
            success = "Rule Updated"

        return render_template(
            'user_edit_rule.html',
            global_config=CONFIG,
            local_config=local_config,
            userdata=userdata,
            ruledata=rule,
            success=success,
            menu_rules=generate_menu_items(),
            error=error
        )


@bp.route('/monitor/rule/<path:rule>', methods=['GET'])
def monitor_rule(rule):
    if not session.get('logged_in'):
        return redirect(url_for('routes.home'))
    else:
        userdata = {
            'fullname': session.get('name'),
            'email': session.get('email'),
            'user_id': session.get('user_id')
        }
        local_config = {
            "page_name": "Edit Monitoring Rule",
            "monitor": True,
            "viewrules": True
        }

        try:
            rule = int(rule)
        except ValueError:
            return error_page("Invalid Rule ID")

        db = get_db_session()
        query = db.query(Rule).\
            filter(and_(Rule.id == rule, Rule.userid == userdata['user_id']))

        try:
            rule = query.one()
        except NoResultFound:
            return error_page("Invalid Rule ID")

        return render_template(
            'user_edit_rule.html',
            global_config=CONFIG,
            local_config=local_config,
            userdata=userdata,
            ruledata=rule,
            success="",
            menu_rules=generate_menu_items(),
            error={"errors": 0, "message": ""}
        )


@bp.route('/monitor/add', methods=['GET', 'POST'])
def monitor_add():
    if not session.get('logged_in'):
        return redirect(url_for('routes.home'))
    else:
        userdata = {
            'fullname': session.get('name'),
            'email': session.get('email'),
            'user_id': session.get('user_id')
        }
        local_config = {
            "page_name": "Add Monitoring Rule",
            "monitor": True,
            "addrules": True
        }
        result = ""
        success = ""
        error = {"errors": 0, "message": ""}
        if request.method == 'POST':
            if not request.form['rulename']:
                error['errors'] += 1
                error['message'] = "Rulename is required"

            if not request.form['keywords']:
                error['errors'] += 1
                error['message'] = "Keywords are required"

            if not request.form['description']:
                error['errors'] += 1
                error['message'] = "Description is required"

            if not request.form['handle']:
                error['errors'] += 1
                error['message'] = "Twitter Handle is required"

            if error['errors'] == 0:
                db = get_db_session()
                rule = Rule(
                    rulename=request.form['rulename'],
                    keywords=request.form['keywords'],
                    account_handle=request.form['handle'],
                    description=request.form['description'],
                    active=1,
                    userid=userdata['user_id']
                )
                db.add(rule)
                db.commit()
                success = "Rule added"

        return render_template(
            'user_addrule.html',
            global_config=CONFIG,
            local_config=local_config,
            userdata=userdata,
            result=result,
            success=success,
            menu_rules=generate_menu_items(),
            error=error
        )


@bp.route('/monitor', methods=['GET', 'POST'])
def monitor():
    if not session.get('logged_in'):
        return redirect(url_for('routes.home'))
    else:
        userdata = {
            'fullname': session.get('name'),
            'email': session.get('email'),
            'user_id': session.get('user_id')
        }
        local_config = {
            "page_name": "Your Monitoring Rules",
            "monitor": True,
            "viewrules": True
        }
        db = get_db_session()
        query = db.query(
            Rule.rulename,
            Rule.keywords,
            Rule.description,
            Rule.active,
            Rule.account_handle,
            Rule.id,
            func.count(Tweet.id).label('total')
        ).filter(
            Rule.userid == userdata['user_id']
        ).join(
            Tweet, isouter=True
        ).group_by(
            Rule.id
        ).order_by(
            Rule.rulename
        )
        rules = query.all()

        return render_template(
            'user_rules.html',
            global_config=CONFIG,
            local_config=local_config,
            userdata=userdata,
            menu_rules=generate_menu_items(),
            rules=rules
        )


@bp.route('/freetext', methods=['GET', 'POST'])
def freetext():
    if not session.get('logged_in'):
        return redirect(url_for('routes.home'))
    else:
        result = ""
        freetext = ""
        if request.method == 'POST':
            if request.form['freetext'] and len(request.form['freetext']) > 0:
                freetext = request.form['freetext']
                sa = SentimentAnalyser()
                result = sa.multinomial_naive_bayes(freetext)

        local_config = {
            "page_name": "Freetext Classifier",
            "home": True,
            "freetext": True
        }
        userdata = {
            'fullname': session.get('name'),
            'email': session.get('email'),
            'user_id': session.get('user_id')
        }
        return render_template(
            'user_freetext.html',
            global_config=CONFIG,
            local_config=local_config,
            userdata=userdata,
            result=result,
            menu_rules=generate_menu_items(),
            freetext=freetext
        )


def generate_menu_items():
    db = get_db_session()
    query = db.query(
        Rule.rulename,
        Rule.id
    ).filter(
        Rule.userid == session.get('user_id'),
        Rule.active == 1
    ).order_by(
        Rule.rulename
    )
    try:
        rules = query.all()
    except NoResultFound:
        rules = []

    return rules


def error_page(message):
    return render_template(
        'error.html',
        message=message
    )
