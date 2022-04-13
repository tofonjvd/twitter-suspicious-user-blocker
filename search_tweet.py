import tweepy
import config

#The $bearer_token should be set to your own bearer_token, I stored them in config.py file.
#You can get your own tokens from Twitter's developer panel.
client = tweepy.Client(bearer_token=config.bearer_token)

#We need two variables for recognizing suspicious tweet and suspicious user.
#The values depend on the project and type of tweets. In this code, if a tweet has more than 1
# suspicious word, it means that the tweet is suspicious and if a user has more than 1 suspicious
#tweets, it means that user is suspicious.
suspecious_words = int()
suspecious_tweet = int()

#In here, you should define the list of your suspicious words.
#You can add more words if you want.
filter_words_list = ["string1", "string2", "string3"]

#We need the $auth for authenticating ourselves for the sake of blocking the suspicious user.
#Again, you can find $api_key, $api_key_secret, $access_token and $access_token_secret in the config.py file.
#Moreover, you must set them with your own tokens.
auth = tweepy.OAuth1UserHandler(config.api_key, config.api_key_secret, config.access_token, config.access_token_secret)

#Here, we are authenticating ourselves.
api = tweepy.API(auth, wait_on_rate_limit=True)

#In V1.0 of this code, I decide to crawl thorough my own followers, so in the next line, I am getting my
#followers list and some specific parameters of those users in the $user_fields.
# ( for more information, check the following link. )
#https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/user
users = client.get_users_followers(id=config.user_id, user_fields=["username", "id", "public_metrics", "name", "protected"])
#Next line is a dummy way to get the tweet counts of a specific user, which is located in the $public_metrics .
user_field_for_tweets_count = "tweet_count"
for user in users.data:
    #I put the next condition, because if the user made his account protected or private, the code
    #will return error.
    if user.protected == False:
        #$suspecious_tweet should reset for each user.
        suspecious_tweet = 0
        #Instead of using the for loop for $tweets, you can also use the following code:
        # tweets = client.get_users_tweets(id=user.id, max_results=100, tweet_fields=["text", "entities", "id"])
        #this line will return you a list of that user's tweets and then you can
        # make a for loop for getting each tweets. But the problem is, in this way, you can only
        #get at most 100 tweets. So if we want to get more than that ( in this case, at most 1000 ), we must use paginator, like the mext for loop.
        #The $client.get_users_tweets method will return us the tweets of the user with the $id of $user.id .
        #We also need some specific information about each tweet in the $tweet_fields .
        #For more information, check the following links:
        #https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet
        #https://developer.twitter.com/en/docs/twitter-api/tweets/timelines/api-reference/get-users-id-tweets
        for tweets in tweepy.Paginator(client.get_users_tweets, id=user.id, max_results=100, tweet_fields=["text", "entities", "id"]).flatten(limit=1000):
            #Again, for the sake of error protection, which will return an empty/null object,
            #we are checking if the user has at least 1 tweet, then we can check that tweet and
            # see if it is suspicious or not.
            if user.public_metrics[user_field_for_tweets_count] != 0:
                #It would be better if I used a while loop instead of for, but I am tired, hungry and feel
                #sleepy now. So in the future updates I will change it.
                #We are checking those information about each tweet so we can filter them.
                for tweet in tweets.data:
                    #Each tweet can or cannot have suspicious words, so it must get reset in each cycle.
                    suspecious_words = 0
                    #We are looping thorough the $filter_words_list and check if each of those
                    #words are in the tweet or not.
                    for filter_words_list_index in range(len(filter_words_list)):
                        if filter_words_list[filter_words_list_index] in tweets.text:
                            #If we have a suspicious word, so the variable should get plus 1.
                            suspecious_words += 1
                #Now, if a tweet has more than 1 suspicious words, it means we have a suspicious tweet.
                if suspecious_words > 1:
                    suspecious_tweet += 1
        #Now, if a user has more than 1 suspicious tweets, BANG! We will block him.
        if suspecious_tweet > 1:
            #For more information about the method, check the following link.
            #https://developer.twitter.com/en/docs/twitter-api/users/blocks/api-reference/post-users-user_id-blocking
            api.create_block(user_id=user.id)
            print(f"USER {user.username} has been blocked !")
