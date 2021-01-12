import run_collaborative_filtering as coll
import run_cluster as clus
import game_theory as gt
import genetic_optimize as gene
import annealing_optimize as ann
import statistics as stat
import MySQLdb as db
import random
import time
import math

# initialize the experiment for first use
def initialize():
    coll.initialize_collaborative_filter()
    clus.initialize_cluster()

# run the experiment`s core, just for game theory.
def run(user_id):
    result_from_coll_filter, movie_had_seen = coll.run_collaborative_filter(user_id)
    result_from_cluster, movie_name_arr = clus.run_cluster()
    
    time_start = record_runtime()
    
    result_dict, sum_of_game_value = gt.run_game_theory(result_from_coll_filter, movie_had_seen, 
                                                        result_from_cluster, movie_name_arr)
    
    time_end = record_runtime()
    time_pass = time_end - time_start
    
    return result_dict, sum_of_game_value, time_pass

# analysis the collaborative filter method, see if game theory method is effective
def origin_coll_filter_analysis(user_id):
    result_from_coll_filter, movie_had_seen = coll.run_collaborative_filter(user_id)
    payoff_list, name_from_coll_result = gt.gen_payoff_coll_filt(result_from_coll_filter)

    print 'collaborative filter analysis finished.'
    return name_from_coll_result, payoff_list

def genetic_plus_opt_analysis(user_id):
    result_from_coll_filter, movie_had_seen = coll.run_collaborative_filter(user_id)
    result_from_cluster, movie_name_arr = clus.run_cluster()
    
    time_start = record_runtime()
    
    name_list_from_genetic, payoff_list_from_genetic = gene.genetic_opt_plus(result_from_coll_filter,
                                                                             movie_had_seen, 
                                                                             result_from_cluster,
                                                                              movie_name_arr)
    
    time_end = record_runtime()
    time_pass = time_end - time_start
    
    print 'genetic_plus optimize analysis finished.'
    return name_list_from_genetic, payoff_list_from_genetic, time_pass

# analysis the annealing optimize method, see if game theory method is effective
def annealing_opt_analysis(user_id):
    result_from_coll_filter, movie_had_seen = coll.run_collaborative_filter(user_id)
    result_from_cluster, movie_name_arr = clus.run_cluster()
    
    time_start = record_runtime()
    
    name_list_from_annealing, payoff_list_from_annealing = ann.annealing_optimize(
                                                    result_from_coll_filter, movie_had_seen, 
                                                    result_from_cluster, movie_name_arr)
    
    time_end = record_runtime()
    time_pass = time_end - time_start
    
    print 'annealing optimize analysis finished.'
    return name_list_from_annealing, payoff_list_from_annealing, time_pass

# analysis the game theory    
def game_theory_analysis( result_dict ):
    # recommend_result use to store the name of the result
    recommend_result_name = []
    # recommend_cost use to store  each result`s expected value of rating
    recommend_result_payoff = []
    # recommend_result _tmp cache the result for addition calculate and compare 
    recommend_result_tmp = []
    
    # fetch the key and value list from the result dictionary passed in, throw
    # away the one whose probability is 0
    for key, val in result_dict.items():
        if val[0] != 0:
            recommend_result_tmp.append( (val[1], key) )
    # sort the temper result by expected value of rating and then reverse
    recommend_result_tmp.sort(cmp=None, key=None, reverse=False)
    recommend_result_tmp.reverse()
    # generate the formal result, each one just a pure list
    for element in recommend_result_tmp:
        recommend_result_name.append(element[1])
        recommend_result_payoff.append(element[0])
    
    print 'game theory optimize analysis finiched.'        
    return recommend_result_name, recommend_result_payoff


def format_result_output(result_list_name, result_list_payoff, time_pass=0):
    print '\n'
    print(result_list_name)
    print '\n'
    print(result_list_payoff)
    print '\n'
    print(time_pass)
    print '\n'

def gen_rand_usr( num_of_usr ):
    # fetch the database to get the numbers of the users
    con = db.connect('localhost', 'root', 'your password', 'movie_data')
    cur = con.cursor()
    cur.execute( """SELECT COUNT( DISTINCT( user_id ) )
                    FROM ratings """)
    usr_sum = cur.fetchone()[0]
    
    rand_usr_list = []
    for i in range( num_of_usr ):
        usr = random.randint( 1, usr_sum )
        rand_usr_list.append(str(usr))
    
    return rand_usr_list

def record_runtime():
    time_spot = time.time()
    
    return time_spot

# built the dictionary from the analysis result
def create_analysis_dict():
    # initial a dictionary to cache the analysis result to draw picture
    method_list = ('game theory', 'genetic optimize', 'annealing optimize', 'collaborative filter')
    attribute_list = ('recommend numbers', 'run time', 'average rating', 'standard deviation')
    
    analysis_result = {}
    for method in method_list:
        analysis_result.setdefault(method, {})
        for attribute in attribute_list:
            analysis_result[method].setdefault(attribute, [])
    
    print analysis_result, '\n'
    return analysis_result

# insert the analysis result into a dictionary
def built_analysis_dict( analysis_result_dict, method, name_list, payoff_list, rtime=0 ):
    reco_num = len(name_list)
    run_time = rtime
    average_rating = sum(payoff_list)/reco_num
    # calculate the standard deviation
    std_dev = calculate_std_dev(payoff_list)
    
    for attribute in analysis_result_dict[method].keys():
        if attribute == 'recommend numbers':
            analysis_result_dict[method][attribute].append(reco_num)
        elif attribute == 'run time':
            analysis_result_dict[method][attribute].append(run_time)
        elif attribute == 'average rating':
            analysis_result_dict[method][attribute].append(average_rating)
        elif attribute == 'standard deviation':
            analysis_result_dict[method][attribute].append(std_dev)
    
    print analysis_result_dict, '\n'        
    return analysis_result_dict
            
# calculate the standard deviation    
def calculate_std_dev(val_list):
    val_num = len(val_list)
    square_sum = 0.0
    avg = float(sum(val_list))/float(val_num)
    for val in val_list:
        square_sum += pow((val - avg), 2)
        
    result = math.sqrt(square_sum / float(val_num))
    
    return result

# fetch the data from the dictionary for later use
def fetch_analysis_dict_for_plot( analysis_dict, attr ):
    x_vec = {}
    y_vec = {}
    x_label = 'random member'
    y_label = ''
    for method, attribute_dict in analysis_dict.items():
        x_vec.setdefault(method, [])
        y_vec.setdefault(method, [])
        for attribute, attribute_list in attribute_dict.items():
            if attr == attribute:
                y_label = attribute
                for i in range( len(attribute_list) ):
                    x_vec[method].append(i)
                    y_vec[method].append(attribute_list[i])
    
    print x_vec, y_vec                
    return x_vec, y_vec, x_label, y_label

def run_all_analysis():
    # assign a user id to run
    num_of_usr = 50
    usr_list = gen_rand_usr(num_of_usr)
    print usr_list
    analysis_result = {}
    analysis_result = create_analysis_dict()
    method_list = ('game theory', 'genetic optimize', 'annealing optimize', 'collaborative filter')
    attribute_list = ('recommend numbers', 'run time', 'average rating', 'standard deviation')
    
    for i in range(len(usr_list)):
        user_id = usr_list[i]

        result_dict, sum_of_game_value, time_game = run(user_id)
        recommend_result_name_gt, recommend_result_payoff_gt = game_theory_analysis( result_dict )
        analysis_result = built_analysis_dict( analysis_result,
                                                method_list[0], recommend_result_name_gt, 
                                                recommend_result_payoff_gt, time_game )
        
        name_from_coll_result, payoff_from_coll = origin_coll_filter_analysis(user_id)
        analysis_result = built_analysis_dict( analysis_result, method_list[3],
                                                name_from_coll_result, payoff_from_coll
                                                )
        
        name_from_genetic, payoff_from_genetic, time_gene = genetic_plus_opt_analysis(user_id)
        analysis_result = built_analysis_dict( analysis_result, method_list[1], 
                                               name_from_genetic, payoff_from_genetic, 
                                               time_gene )
        name_from_annealing, payoff_from_annealing, time_anna = annealing_opt_analysis(user_id)
        analysis_result = built_analysis_dict( analysis_result, method_list[2], 
                                               name_from_annealing, payoff_from_annealing, 
                                               time_anna )
    
        format_result_output( recommend_result_name_gt, recommend_result_payoff_gt, time_game )
        format_result_output( name_from_coll_result, payoff_from_coll )
        format_result_output( name_from_genetic, payoff_from_genetic, time_gene )
        format_result_output( name_from_annealing, payoff_from_annealing, time_anna )
    
    for j in range(len(attribute_list)):
        x_vec, y_vec, x_label, y_label = fetch_analysis_dict_for_plot( analysis_result,
                                                                        attribute_list[j])     
        stat.draw_pic(x_vec, y_vec, x_label, y_label, attribute_list[j])

run_all_analysis()