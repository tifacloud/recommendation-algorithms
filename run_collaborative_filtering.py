import collaborative_filtering as func_set
import MySQLdb as db

def gen_item_dict_from_db():
    # get data from database
    con = db.connect('localhost','root','your password', 'movie_data')
    prefs = {}
    movies = {}

    try:
        cursor = con.cursor()
        cursor.execute("""SELECT  movies.movie_id, movies.movie_name, ratings.user_id, ratings.rating 
                        FROM movies INNER JOIN ratings 
                        ON movies.movie_id = ratings.movie_id""")
        con.commit()
    except db.Error:
        print 'ERROR: start to roll back'
        print db.Error
        try:
            con.rollback()
        except:
            pass

    num_mov = int(cursor.rowcount)

    for i in range(num_mov):
        row = cursor.fetchone()
        movie_id = str(row[0])
        movie_name = str(row[1])
        user_id = str(row[2])
        rating = float(row[3])
    
        movies.setdefault(movie_id, "")
        movies[movie_id] = movie_name

        prefs.setdefault(user_id, {})
        prefs[user_id][movies[movie_id]] = rating 


    cursor.close()
    con.close()
    
    return prefs

# get the item dictionary to generate a item matrix
def gen_item_matrix(prefs):
    itemsim = func_set.calculateSimilarItems(prefs, n=50)
    return itemsim

# store the item matrix to database
def store_item_matrix(itemsim):
    try:
        con = db.connect('localhost', 'root', 'your password', 'movie_data')
    except db.Error:
        print 'failed connect to database'
        print db.Error
        
    # fetch the data to list
    for key, val in itemsim.items():
        movie_name = db.escape_string(key)
        for i in range( len(val) ):
            sim_movie = db.escape_string(val[i][1])
            similarity = float(val[i][0])
            try:
                cur = con.cursor()
                cur.execute("""INSERT INTO item_matrix_cache( movie_name, sim_movie, similarity)
                        VALUES( '%s', '%s', %f )""" % (movie_name, sim_movie, similarity))
                con.commit()
                cur.close()
            except db.Error:
                print 'insert error'
                print db.Error
                try:
                    con.rollback()
                    cur.execute("""UPDATE item_matrix_cache
                                    SET similarity=%f
                                    WHERE movie_name='%s'
                                    AND sim_movie='%s'""" % (similarity, movie_name, sim_movie ))
                    con.commit()
                    cur.close()
                except db.Error:
                    print 'update error'
                    print db.Error
                    pass       
    con.close()
    print 'store item matrix finished.'

# fetch the item matrix from database
def fetch_item_matrix_from_db():
    try:
        con = db.connect('localhost', 'root', 'your password', 'movie_data')
    except db.Error:
        print 'failed connect to database'
        print db.Error
    
    result = {}
    try:
        cur = con.cursor()
        cur.execute("""SELECT movie_name, sim_movie, similarity
                        FROM item_matrix_cache""")
        con.commit()
    except db.Error:
            print 'update error'
            print db.Error
            try:
                con.rollback()
            except db.Error:
                pass
    
    num_mov = int(cur.rowcount)
    for i in range( num_mov ):
        row = cur.fetchone()
        movie_name = str(row[0])
        sim_movie = str(row[1])
        similarity = float(row[2])
        result.setdefault(movie_name, [])
        result[movie_name].append( (similarity, sim_movie) )
        
    cur.close()
    con.close()
    print 'fetch item matrix success.'
    return result

# initialize the collaborative filter, generate the item-item matrix and store in 
# database
def initialize_collaborative_filter():
    prefs = gen_item_dict_from_db()
    item_matrix = gen_item_matrix(prefs)
    store_item_matrix( item_matrix )

# fetch the item-item matrix from database, use it to calculate for recommendation
# return the result for game theory to use
# we can pass a user id instead of a fixed one in order to make the program more usable 
def run_collaborative_filter(user_id):
    prefs = gen_item_dict_from_db()
    itemsim = fetch_item_matrix_from_db()
    result_from_coll_filter = func_set.getRecommendedItems(prefs, itemsim, user_id)[0:50]
    return result_from_coll_filter, prefs[user_id]

