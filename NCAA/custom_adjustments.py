# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 15:41:14 2015

@author: adammihalik
"""
import pandas as pd
import numpy as np

prediction_file = 'predictions/current/base_pred_2015'
custom_file     = 'predictions/current/custom_pred_2015_B3'
teams           = pd.read_csv( 'data/teams.csv', delimiter=',')

custom_yr = 2015
##----------------------------------------
base_predictions    = pd.read_csv( prediction_file, delimiter=',')

def get_teamName( teamID):
    return teams.team_name.values[teams.team_id.values == teamID ][0]

def get_teamID( teamName ):
    return teams.team_id.values[teams.team_name.values == teamName ][0]
    
def print_team_pred( teamName):
    teamId = get_teamID( teamName )
    inds =  np.nonzero( (sub_table[:,0] == custom_yr) & ( (sub_table[:,2] == teamId) | (sub_table[:,1] == teamId) ))[0]
    for idx in inds:
        print get_teamName(sub_table[idx][1]),get_teamName(sub_table[idx][2]), base_predictions.iloc[idx].pred
#break apart sting to get teams and year
sub_table   = np.array( [ (int(k[0:4]), int(k[5:9]),int(k[10:14] ))  for k in base_predictions.id.values ] )
#print_team_pred('Arizona' )

##first make a function that adjust game give 2 teams.
#teams[teams.team_name == 'Connecticut' ]
## A adjustments.
#game_pr = [ ['Kentucky', 'Hampton' , .995],
#            ['Kentucky', 'Manhattan' , .995],
#            ['Kentucky', 'North Florida' , .995],
#            ['Kentucky', 'Purdue' , .995],
#            ['Kentucky', 'Cincinnati' , .995],
#            ['Butler', 'Texas', .6 ],
#            ['Notre Dame', 'Northeastern', .88 ],
#            ['Kansas', 'New Mexico St', .88 ],
#            ['Wisconsin', 'Coastal Car', .99 ],
#            ['Oklahoma St', 'Oregon', .55 ],
#            ['Duke', 'North Florida' , .99],
#            ['Duke', 'Robert Morris' , .99],
#            ['Villanova', 'Lafayette' , .99],
#            ['Virginia', 'Belmont' , .89],
#        ]
#
#team_adj = [ ['Kentucky', 1.15], 
#            [ 'Arizona', 1.1 ]
#            ]
###############################
##b Adjustments.
game_pr = [ ['Kentucky', 'Hampton' , .995],
            ['Kentucky', 'Manhattan' , .995],
            ['Duke', 'North Florida' , .99],
            ['Duke', 'Robert Morris' , .99],
            ['Virginia', 'Belmont' , .90],
            ['Wisconsin', 'Coastal Car', .99 ],
            ['Villanova', 'Lafayette', .99 ],
            ['Villanova', 'LSU', .90 ],
            ['Villanova', 'NC State', .90 ],
            ['Duke', 'North Florida' , .99],
            ['Duke', 'Robert Morris' , .99],
            ['Gonzaga', 'N Dakota St' , .95],
            ['Butler', 'Texas' , .6],
            ['Wyoming', 'Northern Iowa' , .4],
            ['Buffalo', 'West Virginia' , .35],
            ['Louisville', 'UC Irvine' , .85],
            ['Louisville', 'Northern Iowa' , .53],
            ['Kansas', 'New Mexico St' , .9 ],
        ]

team_adj = [ ['Kentucky', 1.65], 
            ]

for cnt in range( len( team_adj )):
    team1 = get_teamID( team_adj[cnt][0] )
    t1 =  np.nonzero( (sub_table[:,0] == custom_yr) & (sub_table[:,1] == team1) )[0]
    base_predictions['pred'][t1]= np.minimum( base_predictions['pred'][t1] * team_adj[cnt][1], .99 )
    print 'changing 1st opp', team_adj[cnt][0], 'up by', team_adj[cnt][1], ',', len(t1), 'games'    
    t2 =  np.nonzero( (sub_table[:,0] == custom_yr) & (sub_table[:,2] == team1) )[0]
    base_predictions['pred'][t2] =  1 - np.minimum( (1- base_predictions['pred'][t2])* team_adj[cnt][1],.99 )
    #base_predictions['pred'][t2]= base_predictions['pred'][t2] * (1./team_adj[cnt][1] )
    print 'changing 2st opp', team_adj[cnt][0], 'down by', (team_adj[cnt][1] ), ',', len(t2), 'games'

##Finally, set specific values for given games.
for cnt in range( len( game_pr ) ):
    team1 = get_teamID( game_pr[cnt][0] )
    team2 = get_teamID( game_pr[cnt][1] )   
    t1 =  np.nonzero( (sub_table[:,0] == custom_yr) & (sub_table[:,1] == team1) & (sub_table[:,2] == team2) )[0]
    if len(t1)>0:
        base_predictions['pred'][t1[0]]= game_pr[cnt][2]
        print game_pr[cnt][0], 'over', game_pr[cnt][1], game_pr[cnt][2]
    t2 =  np.nonzero( (sub_table[:,0] == custom_yr) & (sub_table[:,2] == team1) & (sub_table[:,1] == team2) )[0]
    if len(t2)>0:
        base_predictions['pred'][t2[0]]= 1- game_pr[cnt][2]
        print game_pr[cnt][1], 'over', game_pr[cnt][0], (1 - game_pr[cnt][2] )



###################################################
base_predictions.to_csv(custom_file, index = False )