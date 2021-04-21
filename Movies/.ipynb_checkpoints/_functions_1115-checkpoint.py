from tmdbv3api import TMDb, Movie, Discover
import pandas as pd
import time
from IPython.display import Markdown

tmdb = TMDb()
tmdb.api_key = '0921b0cce35c0b2ec8b874614d1d0b47' ##insert apikey
tmdb.language = 'en'
movie=Movie()
discover=Discover()

def help():
    display(Markdown('''
### Functions:
1. `full_mov_db_2_csv('YYYY-MM-DD')` :   
    Extract daily exports of TMDB database  
2. `consec_dict_2_df(<array_of_similar_dictionaries>)` :  
    Convert an array of dictionaries to a tidy dataframe  
3. `financialstat_counter(<array of movie IDs>)` :  
    Checks percentage of movies that contain financial information.
4. `discover_2_csv(dict_param, output)` :
    Uses TMDBv3's API to extract a csv file containing results that match the search description.
    Also returns a DataFrame for data manipulation
5.  `strtolist(str_in)` :
    Converts a string representation of a list into a list. Data type of elements in list must be the same.
    Accepts string representation of list that contains element strs, ints, or string representation of ints.
    '''))

## Extract daily exports of entire TMBD database
## Function accepts ISO 8601 spec for dates
## e.g. full_mov_db_2_csv('YYYY-MM-DD')
def full_mov_db_2_csv(date):
    ## format the fetch url
    db_online_path='http://files.tmdb.org/p/exports/movie_ids_'+date[5:7]+'_'+date[8:10]+'_'+date[:4]+'.json.gz'
    print("Export link:", db_online_path)
    
    ## will throw exception if url does not exist
    try:
        data_raw = pd.read_json(db_online_path, compression='gzip', lines=True)
        print("Writing to file...")
    except:
        print('Error in extracting file from link...\nFile may not yet exist on TMDB.')
        return
    
    ## format the local file name
    db_path='FullDB_'+date+'.csv'
    data_raw.to_csv(db_path)
    print("Exported to local folder:",db_path)
         
## input param must be a list/array containing multiple dictionaries that use identical keys
## Returns a properly formatted dataframe with the keys at column positions
def consec_dict_2_df(dict_in):
    return_df = None
    for item in dict_in:
        sub_df = pd.DataFrame.from_dict(item, orient='index')
        if return_df is None:
            return_df = sub_df.T
        else:
            return_df = pd.concat([return_df,sub_df.T], sort=True)
    ## reindex dataframe, auto-convert to most suitable datatype
    return return_df.convert_dtypes().reset_index(drop=True)
    
## variable 'data' is the list of movie ids to call to TMDB
## pass the 'id' column from daily export CSV into function
## take the first 10 values and increment by an order of magnitude for each iteration
## >5000 consec api calls and requests will be rate limited
def financialstat_counter(data):
    ## variable 'data' is the list of movie ids to call to TMDB
    hit=0
    total_count=0
    total_uncount=0
    top=len(data)

    for item_id in data:
        ## visual indication of progress
        time.sleep(0.001)
        if total_count+total_uncount == top-1:
            print('API call complete:   '+str(total_count+total_uncount+1)+'/'+str(top))
        else:
            print('API calls: '+str(total_count+total_uncount+1)+'/'+str(top),end = "\r")

        ## skips call if api barfs 
        try:
            mov = movie.details(item_id)
            if(mov['budget'] and mov['revenue']):
                hit += 1
            total_count += 1
        except:
            total_uncount += 1
    
    value=hit/total_count*100
    print("Successful calls:   ",str(total_count))
    print("Unsuccessful calls: ",str(total_uncount))
    print("Percentage of movies with financial statistics: ",str(value)+'%\n')
    return value/100

# Create a function that exports to a csv file:
## Takes the input params:
## - dictionary containing search parameters
## - Output CSV file name
## Continuously go through each search page (max 100, total 2000 movies) until no result is returned (search complete)
## Move these movies into a DataFrame using the dict_2_dataframe function
def discover_2_csv(dict_param, output):
    df_out = None
    call_fail = 0
    
    ## Input validation
    if type(dict_param)!=dict or type(output)!=str:
        print('Error, inputs must be a dictionary and a string')
        return
    
    ## up to 500 pages available to extract, depending on how broad search is. So up to 20*500=10000 movies possible
    for page_no in range(1,501): ## for debugging purposes, change to max=10
        
        ## Set the current page
        dict_param['page']=page_no
        
        ## Get the list
        movie_list = discover.discover_movies(dict_param)
        
        ## Terminate search if most recent page has nothing
        if len(movie_list) == 0:
            break
            
        ## Make the large dataframe
        try:
            if df_out is None:
                df_out = consec_dict_2_df(movie_list)
            else:
                df_out = pd.concat([df_out,consec_dict_2_df(movie_list)],sort=True)
        except:
            call_fail += 1
        
        ## Output statements to keep track of things
        print('Page number: '+str(page_no)+'/500', end='\r')
    
    ## Resetting the index to count normally
    df_out.reset_index(drop=True, inplace=True)
    print('\nSearch complete\n'+str(page_no*20)+' movies found')
    print(str(len(df_out))+' movies returned')
    print(str(call_fail)+' calls did not get through')
    df_out.to_csv(output)
    print("Exported to local folder:",output)
    return df_out

## Take in a string representation of a list and returns a list containing said elements
## Elements can be string or int data type, ints can be in string form as well
def strtolist(str_in):
    ## if input is indeed a string
    if (str(str_in)):
        returnlist = []
        
        tmp = str_in.strip("[]''")
        #print(tmp)
        tmp = tmp.split(", ")
        #print(tmp)
        
        ## if str representation of list contains nothing, return empty list
        if len(tmp)==1 and len(tmp[0])==0:
            return []
        
        ## attept int conversion
        try:
            for item in tmp:
                returnlist.append(int(item))
        ## Do str processing instead
        except:
            for item in tmp:
                try:
                    returnlist.append(int(item.strip('''"''"''')))
                except:
                    returnlist.append(item.strip('''"''"'''))
                    
        return returnlist