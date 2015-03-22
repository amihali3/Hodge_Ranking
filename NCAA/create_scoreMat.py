# -*- coding: utf-8 -*-
"""
Created on Sat Feb 28 23:07:44 2015

@author: adammihalik
"""

import numpy as np
from geo_ranking import rankSeason
import pandas as pd

createTable = True
rankyears = range( 2003, 2015 )
rs_games    = pd.read_csv( '/Users/adammihalik/Desktop/ranking/data/regular_season_detailed_results.csv', delimiter=',')
teams       = pd.read_csv( '/Users/adammihalik/Desktop/ranking/data/teams.csv', delimiter=',')
tour_res    = pd.read_csv( '/Users/adammihalik/Desktop/ranking/data/tourney_compact_results.csv', delimiter=',' )
seeds       = pd.read_csv( '/Users/adammihalik/Desktop/ranking/data/tourney_seeds.csv', delimiter=',')
sample_sub  = pd.read_csv( 'Data/sample_submission.csv' )
# no more than 364 teams, which is the size of the matrix, max( teams.team_id ) - min( teams.team_id ) + 1
#set-up teams to have matrix indicies for team numbers.
rs_games.wteam = rs_games.wteam - min( teams.team_id ) 
rs_games.lteam = rs_games.lteam - min( teams.team_id ) 
tour_res.wteam = tour_res.wteam - min( teams.team_id )
tour_res.lteam = tour_res.lteam - min( teams.team_id ) 
seeds.team     = seeds.team -  min( teams.team_id )
teams.team_id  = teams.team_id - min( teams.team_id )

#Year, seed1, pwr1a, pwr1b, seed2, pwr2a, pwr2b, team1win?
scoreMat =  np.empty( (0,8 ))
#np.zeros( shape = ( 2*sum([i in rankyears for i in tour_res.season.values ]), 8 ))
for rankyear in rankyears:
    print rankyear

    scr, rnk =  rankSeason( rs_games[ rs_games.season == rankyear-1], teams,[], [], [], rerank = [1000,2000,3000], show_results =False)
    for cnt in np.arange(5):
        scr, rnk =  rankSeason( rs_games[ rs_games.season == rankyear], teams, rnk[1:15], rnk[1:40], rnk[225:],
                               rerank = [1000,2000,3000], show_results =False) 
    scr, rnk =  rankSeason( rs_games[ rs_games.season == rankyear], teams, rnk[1:15], rnk[1:40], rnk[225:],
                               rerank = [1000,2000,3000], show_results =True) 
    if createTable:
        t_yr = tour_res[ tour_res.season ==  rankyear]
        s_yr = seeds[ seeds.season == rankyear]
        for cnt in range(len( t_yr ) ):
            gm = t_yr.values[cnt,:]
            diff = gm[3] - gm[5]
            s1 = int( s_yr.seed.values[ s_yr.team.values == gm[2] ][0][1:3] ) #seed of first team
            s2 = int( s_yr.seed.values[ s_yr.team.values == gm[4] ][0][1:3] ) #seed of 2nd team
            p1a = scr[gm[2]][0] #year long pwr score of first team
            p2a = scr[gm[4]][0] #year long pwr score of 2nd team
            p1b = scr[gm[2]][1] #harmonic score of first team
            p2b = scr[gm[4]][1] #harmonic score of 2nd team
            scoreMat = np.vstack( ( scoreMat, np.array( [int(rankyear), s1, p1a, p1b, s2, p2a, p2b, 1] ) ) )
            scoreMat = np.vstack( ( scoreMat, np.array( [int(rankyear), s2, p2a, p2b, s1, p1a, p1b, 0] ) ) )
            if rankyear<2013 and diff > 15: # double count blow-outs for training.
                for dcnt in range( diff/15 ):            
                    scoreMat = np.vstack( ( scoreMat, np.array( [int(rankyear), s1, p1a, p1b, s2, p2a, p2b, 1] ) ) )
                    scoreMat = np.vstack( ( scoreMat, np.array( [int(rankyear), s2, p2a, p2b, s1, p1a, p1b, 0] ) ) )
                    print ('%i %s %.2f def %i %s %.2f' %
                    (s1,teams.team_name[gm[2]], p1a,
                     s2, teams.team_name[gm[4]], p2a
                     ) )

np.savetxt( 'model_data_processed_harmonic', scoreMat, delimiter="," )