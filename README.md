# football-transfers
The goal of this project is to make an analysis of the football market evolution (from 1992 to 2020) considering the market as a complex network.
The network was generated considering the european clubs as vertexes and the transfers as edges. We considered two approaches to weight the edges:

1. The number of transfers
2. The money involved in the transfers

This is how the network looks like in 2015:

![Alt text](plot_2015.png?raw=true "Plot 2015")

Many evaluation and metrics were used in the analysis. In particular, we used the techinuqes of [Functional cartography of complex metabolic networks](https://www.nature.com/articles/nature03288) in order to evaluate the centrality, partecipation and the score of the teams in the network. A deep analysis of the network communities was also performed using the [fastgreedy algorithm]( http://www.arxiv.org/abs/cond-mat/0408187). 

We used igraph and python. Each of the notebooks in this repository contains a specific analysis properly commented.
