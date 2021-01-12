from operator import add, neg
import MySQLdb as db
import random

# create or get the payoff matrix, pass in two list: payoff1(as row), payoff2(as column)
def gen_payoff_matrix( payoff1, payoff2 ):
    payoff_matrix = []
    # travel the payoff1
    for i in range( len(payoff1) ):
        row_payoff = []
        # travel the payoff2
        for j in range( len(payoff2) ):
            payoff = 0
            payoff = payoff1[i] - payoff2[j]
            # construct the column of the payoff matrix
            row_payoff.append(payoff)
        # construct the row of the payoff matrix
        payoff_matrix.append(row_payoff)
    # return the result
    #print payoff_matrix
    return payoff_matrix

# calculate the payoff matrix to get the odd for the two player(two strategy)
def solve(payoff_matrix, iterations=100):
    'Return the oddments (mixed strategy ratios) for a given payoff matrix'
    transpose = zip(*payoff_matrix)
    numrows = len(payoff_matrix)
    numcols = len(transpose)
    row_cum_payoff = [0] * numrows
    col_cum_payoff = [0] * numcols
    colpos = range(numcols)
    rowpos = map(neg, xrange(numrows))
    colcnt = [0] * numcols
    rowcnt = [0] * numrows
    active = 0
    for i in xrange(iterations):
        rowcnt[active] += 1        
        col_cum_payoff = map(add, payoff_matrix[active], col_cum_payoff)
        active = min(zip(col_cum_payoff, colpos))[1]
        colcnt[active] += 1       
        row_cum_payoff = map(add, transpose[active], row_cum_payoff)
        active = -max(zip(row_cum_payoff, rowpos))[1]
    value_of_game = (max(row_cum_payoff) + min(col_cum_payoff)) / 2.0 / iterations
    return rowcnt, colcnt, value_of_game

# from a strategy name list, find the list of the winning value of the strategy
def gen_payoff_list( name_list ):
    winning_list = []
    # from the name list generate the payoff list use database
    try:
        con = db.connect('localhost', 'root', 'your password', 'movie_data')
    except db.Error:
        print "fail to connect the database."
        print db.Error
    
    for j in range( len(name_list) ):
        name = name_list[j]
        name = db.escape_string(name)
        try:
            cursor = con.cursor()
            cursor.execute("""SELECT ratings.rating 
                                FROM movies INNER JOIN ratings 
                                ON movies.movie_id = ratings.movie_id
                                WHERE movies.movie_name = '%s' """ % (name) )
            con.commit()
        except db.Error:
            print 'ERROR: start to roll back'
            print db.Error
            try:
                con.rollback()
            except:
                pass
            
        num_mov = int(cursor.rowcount)
        winning_score = 0
        score_list = {}
        
        for i in range( num_mov ):
            row = cursor.fetchone()
            row = str(row[0])
            score_list.setdefault(row, 0)
            score_list[row] += 1

        sum = 0.0
        div = 0.0
        for key,val in score_list.items():
            key = float(key)
            sum += key * val
            div += val
        winning_score = float(sum) / float(div)
            
        winning_list.append(winning_score)
    
    return winning_list        


# get the biggest payoff from the database use the name in the strategy list
# for the strategy from collaborative filter
def gen_payoff_coll_filt( result_coll_filt):
    name_from_result = []
    payoff_list = []
    # get name list of the result from collaborative filter
    for i in range( len(result_coll_filt) ):
        name_from_result.append(result_coll_filt[i][1])
        
    payoff_list = gen_payoff_list( name_from_result )
    
    #print payoff_list
    #print '\n'
    #print name_from_result        
    return payoff_list, name_from_result

# for the strategy from cluster, need pass in result from cluster include movie name
# array, and the name array generated from the gen_payoff_coll_filt() function.
def gen_payoff_cluster( result_cluster, movie_name_arr, name_arr_from_coll_filter, movie_had_seen ):
    # use a list to store the strategy name of the payoff
    name_from_result = []
    payoff_list = []
    # loop the name array return from collaborative filter to fetch the similar element
    # from the cluster to form a new name array list with the same length with the name
    # list from the collaborative filter
    for i in range( len(name_arr_from_coll_filter) ):
        name_coll = name_arr_from_coll_filter[i]
        # loop the cluster to find the similar element
        for j in range( len(result_cluster) ):
            # use a flag variable to mark if there is a match
            flag = 0
            for k in result_cluster[j]:
                if name_coll == movie_name_arr[k]:
                    flag = 1
            if flag == 1:
                for round in range(10000):
                    rand_loc = random.randint(0, len(result_cluster[j])-1 )
                    location = result_cluster[j][rand_loc]
                    if movie_name_arr[location] not in movie_had_seen.keys():
                        name_from_result.append(movie_name_arr[location])
                        break
    
    payoff_list = gen_payoff_list( name_from_result )
    
    #print payoff_list
    #print '\n'
    #print name_from_result  
    return payoff_list, name_from_result

# run the game theory to get the combination of collaborative filter and cluster
def run_game_theory(result_from_coll_filter, movie_had_seen, result_from_cluster, movie_name_arr ):
    payoff_list_coll = []
    name_from_list_coll = []
    payoff_list_cluster = []
    name_from_list_cluster = []
    payoff_matrix = []
    result_dict = {}
    result_dict_coll = {}
    result_dict_clust = {}
    sum_of_game_value = 0
    
    payoff_list_coll, name_from_list_coll = gen_payoff_coll_filt( result_from_coll_filter )
    # construct the strategy for collaborate filter to use in game
    for i in range( len(name_from_list_coll) ):
        result_dict.setdefault( name_from_list_coll[i], [0.0,payoff_list_coll[i]] )
        result_dict_coll.setdefault( name_from_list_coll[i], [0.0,payoff_list_coll[i]])
    
    # construct the strategy for cluster to use in game, cluster strategy is built from
    # the strategy of collaborative filter, fetch each of the collaborative filter strategy
    # to search every cluster to find a similar one again and again to form the cluster`s 
    # strategy.when finish construct the two strategy, run the game k times to calculate 
    # the probability of each strategy in the two method.    
    for k in range(100):
        payoff_list_cluster, name_from_list_cluster = gen_payoff_cluster( result_from_cluster,
                                                                          movie_name_arr,
                                                                          name_from_list_coll,
                                                                          movie_had_seen )
        for j in range( len(name_from_list_cluster) ):
            result_dict.setdefault( name_from_list_cluster[j], [0.0,payoff_list_cluster[j]] )
            result_dict_clust.setdefault( name_from_list_cluster[j], [0.0,payoff_list_cluster[j]] )
        # run the game of the two player
        payoff_matrix = gen_payoff_matrix( payoff_list_coll, payoff_list_cluster )
        rowcnt, colcnt, value_of_game = solve( payoff_matrix )
        # sum the probability of each strategy of collaborative filter
        for i in range( len(name_from_list_coll) ):
            row_sum = sum( rowcnt )
            result_dict[name_from_list_coll[i]][0] += ( float(rowcnt[i]) / float(row_sum) )
            result_dict_coll[name_from_list_coll[i]][0] += ( float(rowcnt[i]) / float(row_sum) )
        # sum the probability of each strategy of cluster
        for j in range( len(name_from_list_cluster) ):
            col_sum = sum( colcnt )
            result_dict[name_from_list_cluster[j]][0] += ( float(colcnt[j]) / float(col_sum) )
            result_dict_clust[name_from_list_cluster[j]][0] += ( float(colcnt[j]) / float(col_sum) )
    
        sum_of_game_value += value_of_game

    return result_dict, sum_of_game_value


