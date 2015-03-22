# -*- coding: utf-8 -*-
"""
Given a matrix M, geo_ranking( M ) returns a vector x such that
M - rankGrad( x ) is minimized.

@author: adammihalik
"""
import numpy as np
import scipy.optimize

def rankGrad( rank_vector ):
    return np.subtract.outer( rank_vector, rank_vector ).T

def geo_rank( M ):
    
    def rankErrorGrad( rank_vector ):
        return 2*( -sum(M - rankGrad( rank_vector)) + sum( (M - rankGrad( rank_vector)).T  ) )
    def rankError( rank_vector ):
        return np.sum( (M - rankGrad( rank_vector))**2)
    
    best_x_vec = scipy.optimize.fmin_bfgs(
        f   = rankError,
        x0  = np.zeros( shape= ( M.shape[0] ) ),
        fprime= rankErrorGrad,
        maxiter= 50,
        disp = False
        )
    return best_x_vec
    
def rankSeason( rs_games, teams, aprioriTop, aprioriStrong, aprioriBad,
               rerank = [] ,show_results =False):
    #now adjust strong and Bad every 500 games or so.  pac 10 is getting fcked.
    M = np.zeros( shape = (len( teams ),len( teams ) ) )
    # H is used to calculate the harmonic component of the ranking.    
    H = np.zeros( shape = (len( teams ),len( teams ) ) )
    wins, losses  = np.zeros( len( teams )), np.zeros( len( teams ))
    qwins, blosses = np.zeros( len( teams )), np.zeros( len( teams ))
    topw, bo = np.zeros( len( teams )),np.zeros( len( teams ))
    for i in np.arange(len( rs_games ) ):
        l, w,  =     rs_games.lteam.values[i], rs_games.wteam.values[i]
        ptdiff = rs_games.wscore.values[i]-rs_games.lscore.values[i] 
        wins[w] += 1
        losses[l] += 1
        #decay        
        M[ :, [l,w]  ] *= .995
        M[ [l,w], :  ] *= .995
        #if loser sucks        
        w_adj = .5 if rs_games.lteam.values[i] in aprioriBad else 1
        #home court adjust
        hwn_adj = 1 if rs_games.wloc.values[i] =='N' else .8 if rs_games.wloc.values[i] =='H' else 1.2 
        #apply outcome        
        M[ l, w  ] += hwn_adj * w_adj
        M[ w, l  ] -= hwn_adj * w_adj
        #drift if you beat a good team or lose to bad team        
        if rs_games.lteam.values[i] in aprioriTop:
            M[ :, w  ] += .004
            M[ w, :  ] -= .004
            topw[w] += 1
        if rs_games.lteam.values[i] in aprioriStrong:
            M[ :, w  ] += .0025
            M[ w, :  ] -= .0025     
            qwins[w] += 1
        if rs_games.wteam.values[i] in aprioriBad:
            M[ :, l  ] -= .004
            M[ l, :  ] += .004         
            blosses[l] += 1
        if ptdiff>20:
            M[ :, l  ] -= .005 * (i < 1500)
            M[ l, :  ] += .005 * (i < 1500)
            bo[l] += 1
        if i in rerank:
            pwr_scr = geo_rank(M)
            rankInds = np.argsort( -pwr_scr )
            aprioriTop = rankInds[1:15]            
            aprioriStrong = rankInds[1:40]
            aprioriBad    = rankInds[150:]
            
    pwr_scr = geo_rank(M)
    pwr_scr = pwr_scr - np.mean( pwr_scr )
    H = (M - rankGrad( pwr_scr )  )  
    pwr_scr2 = np.std( (H), axis = 0 )
    pwr_scr2 = pwr_scr2 - np.mean( pwr_scr2 )
    pwr_scr = pwr_scr/np.std( pwr_scr )    
    pwr_scr2 = pwr_scr2/np.std( pwr_scr2 )    
    rankInds = np.argsort( -pwr_scr )
    if show_results:    
        for i in np.arange(35):
            print( '%i: %s %.2f, %.2f Record %i - %i, %i tw, %i qw, %i bl, %i bo' %
            (i+1,  teams.team_name.values[rankInds[i]], pwr_scr[rankInds[i]],pwr_scr2[rankInds[i]],
             wins[rankInds[i]], losses[rankInds[i]], 
             topw[rankInds[i]], qwins[rankInds[i]], blosses[rankInds[i]], bo[rankInds[i]]  )
             )
    return np.array( [pwr_scr, pwr_scr2, wins, losses, topw, qwins, blosses, bo]).T, rankInds