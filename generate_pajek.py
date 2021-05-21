import pandas as pd
import csv
import os
from edgelist2pajek import edgelist_to_pajek

df_all_transfers = pd.read_csv('resources/transfers_clean.csv')
df_buyer     = pd.read_csv('resources/buyer_club_nodes.csv')
df_seller    = pd.read_csv('resources/seller_club_nodes.csv')


def write_pajek(filename, df):
 
    clubs_idx = df['buyer'].append(df['seller'])
    clubs_idx = clubs_idx.unique()
    clubs_idx.sort()
    with open(filename, 'w') as outf:
        print('*Vertices\t{}'.format(clubs_idx.size), file=outf)
        vert_dict = {}
        for i, c in enumerate(clubs_idx):
            if c <= 331:
                club_name = df_buyer.iloc[c-1]['club_name']         
            else:
                club_name = df_seller.iloc[c-332]['club_involved_name']+'_seller'
            vert_dict[c] = i+1
            print('\t{} "{}"'.format(i+1, club_name), file=outf)     
        print('*Edges', file=outf)
        for i in range(df.shape[0]):
            buyer  = vert_dict[df['buyer'].iloc[i]]
            seller = vert_dict[df['seller'].iloc[i]]
            weight = df['weight'].iloc[i]
            print('\t{}\t{}\t{}'.format(buyer, seller, float(weight)), file=outf)



def generate_pajek(year_from, year_to):

    # Filter transfers depending on input
    df_transfers = df_all_transfers[(df_all_transfers['year'] >= year_from) & (df_all_transfers['year'] <= year_to)]

    # Create directory if it does not exist
    path = 'nets/{}-{}'.format(year_from, year_to)
    if not os.path.exists(path):
        os.mkdir(path)

    # Generate edge list (freq)
    df_freq_net = df_transfers[['club_name', 'club_involved_name']].reset_index()
    df_freq_net = df_freq_net.groupby(['club_name', 'club_involved_name']).index.count().reset_index()
    df_freq_net = pd.merge(df_freq_net, df_buyer, how='inner', on='club_name')
    df_freq_net = pd.merge(df_freq_net, df_seller, how='inner', on='club_involved_name')
    df_freq_net.rename(columns={'node_x': 'buyer', 'node_y': 'seller', 'index': 'weight'}, inplace=True)

    # Generate edge list (fee)
    df_fee_net = df_transfers[['club_name', 'club_involved_name', 'fee_cleaned']]
    df_fee_net = df_fee_net.groupby(['club_name', 'club_involved_name']).fee_cleaned.sum().reset_index()
    df_fee_net = pd.merge(df_fee_net, df_buyer, how='inner', on='club_name')
    df_fee_net = pd.merge(df_fee_net, df_seller, how='inner', on='club_involved_name')
    df_fee_net.rename(columns={'node_x': 'buyer', 'node_y': 'seller', 'fee_cleaned': 'weight'}, inplace=True)

    # Generate pajek files
    write_pajek(os.path.join(path, 'freq_net.net'), df_freq_net)
    write_pajek(os.path.join(path, 'fee_net.net'), df_fee_net)


if __name__ == '__main__':

    again = 'y'
    while again == 'y':
        print('Generate network for an interval of years')
        year_from = int(input('From year:'))
        year_to   = int(input('To year:'))
        generate_pajek(year_from, year_to)
        print('Generation done')
        again = input('Again?(y/n)')


