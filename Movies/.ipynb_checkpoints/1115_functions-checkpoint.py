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
    return value


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
    return return_df.convert_dtypes().reset_index()