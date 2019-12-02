import json
import random
import string
import pandas as pd
import numpy as np


from sklearn.metrics.pairwise import cosine_similarity

list_to_delete = [
    'a circular groove. At its best (the triumphant I Wish)',
    'an unlikely record to kick back to',
    'echolocation',
    'her songs engage and challenge us to understand',
    'her wonderfully lush',
    'mixer Jim Waters (Sonic Youth',
    'packing in more drama',
    'past his prime and no longer winning medals',
    'Ys',
    '? by Nena',
    '...And the Beat Goes on',
    ' and &quot',
    'R&amp',
    '&amp',
    '&quot',
    '72 &amp',
    'the droning Shockwave',
    '&amp',
    'the jump from 1975\s Genesis-like Song for America to the corporate pop of 1984\s Perfect Lover is jarring at best',
    'the re-recorded version of Gotta Get Thru This',
    'void of course']

title_dict = np.load('map_tilte.npy', allow_pickle=True).tolist()

to_delete = ['B00008EQCX', 'B000002WT1', 'B0000032GH', 'B0000047D1', 'B000007WJD', 'B000BTFZLE']


'''Dataset'''

def create_and_clean_metadata():

    metadata_df = pd.read_csv('amazon_music_metadata.csv', low_memory=False)

    metadata_df = metadata_df[~metadata_df['title'].isin(list_to_delete)]

    for col in metadata_df.select_dtypes(include=('float64', 'int64')):

        if max(metadata_df[col]) < 1:

            metadata_df = metadata_df.drop(columns=col)

    metadata_df = metadata_df.fillna(0)

    for index in metadata_df.index:

        if len(metadata_df['asin'][index]) != 10:

            to_delete.append(metadata_df['asin'][index])

    metadata_df = metadata_df[~metadata_df['asin'].isin(to_delete)]

    return metadata_df


def create_and_clean_music(df1):

    file = [json.loads(line) for line in open('Digital_Music_5.json', 'r')]

    music_df = pd.DataFrame.from_dict(file)

    music_df = music_df.dropna()
    music_df = music_df.reset_index(drop=True)

    indexNames = music_df.groupby('reviewerID').count() < 20

    index_list = []

    for index in indexNames.index:

        if indexNames['asin'][index]:

            index_list.append(index)

    music_df = music_df[~music_df['reviewerID'].isin(index_list)]

    met_list = df1['asin'].sort_values().unique().tolist()
    music_df = music_df[music_df['asin'].isin(met_list)]
    music_df = music_df[['reviewerID', 'asin', 'reviewerName', 'overall']]

    return music_df


def create_user_key(string_length):

    signs = string.ascii_uppercase + string.digits

    while True:

        user_key = ''.join(random.choice(signs) for i in range(string_length))

        if user_key in users:

            return False

        else:

            return user_key


'''Cosine Similariry'''


def cosine_similarity_function(df, df_index):

    cos = cosine_similarity(df)

    cos_sim = pd.DataFrame(cos, index=df_index, columns=df_index)

    return cos_sim


'''Prediction'''


def item_prediction(df1, df2, user, user_col, item_col, item_rat, item_title, lim):
    '''df1 = music, df2 = metadata'''

    liked_songs = df1[item_col][(df1[user_col] == user) & (df1[item_rat] > 3)].tolist()

    similar_songs = []

    for song in liked_songs:

        sim_somgs = item_sim[item_sim[song] > lim].index

        similar_songs = [*similar_songs, *sim_somgs]

    similar_songs = list(set(similar_songs))

    print('How many new songs you want?')

    counter_lim = input()
    list_of_sim = []

    for song in similar_songs:

        list_of_sim.append(df2[item_title][df2[item_col] == song].to_string(index=False))

    recomends = np.random.choice(list_of_sim, int(counter_lim))

    print('The user {} may like:'.format(user))

    for song in recomends:

        print(song)

    list_of_sim.clear()


metadata = create_and_clean_metadata()
music = create_and_clean_music(metadata)


users = music['reviewerID'].sort_values().unique()
all_music = dict(zip(metadata['asin'].unique(), metadata['title']))

item_sim = cosine_similarity_function(metadata.select_dtypes(include=('float64', 'int64')), metadata['asin'].tolist())

new_user = create_user_key(14)

print('Enter your name please')
user_name = input()

list_of_rats = []
counter = 0

while counter < 5:

    rand_song = random.choice(list(all_music.items()))
    print('Please rate for this song: {}'.format(rand_song[1]))
    rat = input()
    use_asin = rand_song[0]

    if int(rat) > 5:

        print('Please rate in scale from "1" to "5", or type "0" if you haven`t listened this song')
        rat = input()

    if int(rat) > 0:

        list_of_rats.append([new_user, use_asin, user_name, int(rat)])
        counter = len(list_of_rats) + 1

music = music.append(pd.DataFrame((list_of_rats[i] for i in range(len(list_of_rats))), columns=['reviewerID', 'asin', 'reviewerName', 'overall']), ignore_index=True)

item_prediction(music, metadata, new_user, 'reviewerID', 'asin', 'overall', 'title', 0.8)
