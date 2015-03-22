# -*- coding: utf-8 -*-
"""
Produce the data for modeling the game that will be submitted.
"""

import numpy as np
from geo_ranking import rankSeason
import pandas as pd


rankyears = [2015] #range( 2011, 2015 )
rs_games    = pd.read_csv( 'Data/regular_season_detailed_results_2015.csv', delimiter=',')
teams       = pd.read_csv( 'Data/teams.csv', delimiter=',')
seeds       = pd.read_csv( 'Data/tourney_seeds_2015.csv', delimiter=',')
sample_sub  = pd.read_csv( 'Data/sample_submission_2015.csv' )

sub_table   = np.array( [ (int(k[0:4]), int(k[5:9]),int(k[10:14] ))  for k in sample_sub.id.values ] )


# no more than 364 teams, which is the size of the matrix, max( teams.team_id ) - min( teams.team_id ) + 1
#set-up teams to have matrix indicies for team numbers.
rs_games.wteam = rs_games.wteam - min( teams.team_id ) 
rs_games.lteam = rs_games.lteam - min( teams.team_id ) 
sub_table[:,1:] = sub_table[:,1:] -  min( teams.team_id )
seeds.team     = seeds.team -  min( teams.team_id )
teams.team_id  = teams.team_id - min( teams.team_id )

#Year, seed1, pwr1a, pwr1b, seed2, pwr2a, pwr2b, team1win?
scoreMat =  np.empty( (0,7 ))
#np.zeros( shape = ( 2*sum([i in rankyears for i in tour_res.season.values ]), 8 ))
for rankyear in rankyears:
    print rankyear

    scr, rnk =  rankSeason( rs_games[ rs_games.season == rankyear], teams,[], [], [], rerank = [1000,2000,3000], show_results =False)
    for cnt in np.arange(5):
        scr, rnk =  rankSeason( rs_games[ rs_games.season == rankyear], teams, rnk[1:15], rnk[1:40], rnk[225:],
                               rerank = [1000,2000,3000], show_results =False) 
    scr, rnk =  rankSeason( rs_games[ rs_games.season == rankyear], teams, rnk[1:15], rnk[1:40], rnk[225:],
                               rerank = [1000,2000,3000], show_results =True) 
                               
    t_yr = sub_table[sub_table[:,0] ==  rankyear]
    s_yr = seeds[ seeds.season == rankyear]
    for cnt in range(len( t_yr ) ):
        gm = t_yr[cnt,:]
        s1 = int( s_yr.seed.values[ s_yr.team.values == gm[1] ][0][1:3] ) #seed of first team
        s2 = int( s_yr.seed.values[ s_yr.team.values == gm[2] ][0][1:3] ) #seed of 2nd team
        p1a = scr[gm[1]][0] #year long pwr score of first team
        p2a = scr[gm[2]][0] #year long pwr score of 2nd team
        p1b = scr[gm[1]][1] #year long pwr score of first team
        p2b = scr[gm[2]][1] #year long pwr score of 2nd team
        scoreMat = np.vstack( ( scoreMat, np.array( [int(rankyear), s1, p1a, p1b, s2, p2a, p2b] ) ) )

np.savetxt( 'processed_2015', scoreMat, delimiter="," )