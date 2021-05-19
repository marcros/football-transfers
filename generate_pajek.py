import pandas as pd
import csv
import os
from edgelist2pajek import edgelist_to_pajek


def generate_pajek(year_from, year_to):
    # Generate buyer and seller nodes
    df_transfers = pd.read_csv('resources/transfers_clean.csv')
    df_buyer = pd.read_csv('resources/buyer_club_nodes.csv')
    df_seller = pd.read_csv('resources/seller_club_nodes.csv')

    # Filter transfers depending on input
    df_transfers = df_transfers[(df_transfers['year'] >= year_from) & (df_transfers['year'] <= year_to)]

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
    df_freq_net = df_freq_net[['buyer', 'seller', 'weight']]
    df_freq_net.to_csv(os.path.join(path, 'edge_list_freq.txt'), sep="\t",
                       quoting=csv.QUOTE_NONE, index=False, header=False)

    # Generate edge list (fee)
    df_fee_net = df_transfers[['club_name', 'club_involved_name', 'fee_cleaned']]
    df_fee_net = df_fee_net.groupby(['club_name', 'club_involved_name']).fee_cleaned.sum().reset_index()
    df_fee_net = pd.merge(df_fee_net, df_buyer, how='inner', on='club_name')
    df_fee_net = pd.merge(df_fee_net, df_seller, how='inner', on='club_involved_name')
    df_fee_net.rename(columns={'node_x': 'buyer', 'node_y': 'seller', 'fee_cleaned': 'weight'}, inplace=True)
    df_fee_net = df_fee_net[['buyer', 'seller', 'weight']]
    df_fee_net.to_csv(os.path.join(path, 'edge_list_fee.txt'), sep="\t",
                      quoting=csv.QUOTE_NONE, index=False, header=False)

    # Generate pajek files
    edgelist_to_pajek(os.path.join(path, 'edge_list_freq.txt'), os.path.join(path, 'freq_net.net'), weighted=True)
    edgelist_to_pajek(os.path.join(path, 'edge_list_fee.txt'), os.path.join(path, 'fee_net.net'), weighted=True)


# Generate net files for the desired period
generate_pajek(2017, 2019)


