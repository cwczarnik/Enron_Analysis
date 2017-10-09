## Christian Hansen
## RedOwl Data Challenge
## September 6th 2017

## ENRON top sender time series analysis
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys

script = sys.argv[0]
filename = sys.argv[1]

def load_in_and_clean_columns(file_name):
    # loads in enron data in local folders and makes unique time files
    enron_df = pd.read_csv('./'+file_name)
    enron_df.columns = ['time','message_id','sender','recipients','topic','mode']
    ## change time to regular from unix time
    enron_df['time']=pd.to_datetime(enron_df['time'],unit='ms')
    # change time to seperate values of time increments
    enron_df['year']=enron_df['time'].dt.year
    enron_df['day']=enron_df['time'].dt.day
    enron_df['date']=enron_df['time'].dt.date
    enron_df['weekday']=enron_df['time'].dt.weekday
    enron_df['month']=enron_df['time'].dt.month
    # add counter to evaluate counts over time
    enron_df['count']=1
    print( enron_df.shape)
    return(enron_df)

enron_df  =  load_in_and_clean_columns(filename)
print(enron_df.head())


def get_person_sent_rec(input_df = enron_df):
    rec = enron_df['recipients'].value_counts().reset_index()
    send = enron_df['sender'].value_counts().reset_index()
    df = pd.merge(send,rec,how='inner',on='index').sort_values('sender',ascending=False)
    df.columns = ['person','sender_count','recipients_count']
    df.to_csv('person_sent_recieved_count.csv')
    return(df)

person_sent_rec_df = get_person_sent_rec(enron_df)
## From the initial dataframe extracting the top ten most prolific senders of emails.
## Global array variable:
top_ten_sender = enron_df['sender'].value_counts().reset_index()['index'][0:10]


def plot_times_sent(df,sender_bool,color = ['grey','green','blue','maroon','teal'],a=0.9):
    # Plot time information for a specified in slice of dataframe for sender
    plt.figure(figsize=(30,5))
    if sender_bool== True:
        name = df.iloc[0]['sender']
        print(name)
    else:
        name ='Total Time Series'
        print(name)
    
    # plot total date 
    plt.subplot(1,5,1)
    df.groupby('date')['sender'].count().plot(kind = 'area',title = 'Counts versus Date',color =color[0],alpha =a,rot =80)
    ax =plt.subplot(1,5,2)
    ## year has issues with ticks so I'll specify ticks better
    date_grouped = df.groupby('year')['sender'].count()
    date_grouped.plot(kind = 'area',title = 'Count versus Year',color=color[1],alpha =a)
    ax.set_xticks(date_grouped.reset_index().year)
    ax.set_xticklabels(date_grouped.reset_index().year)
    ## for the following time increments, where day is day per month,
    #looping through the values makes the most sense to conserve space
    time_list = ['month','weekday','day']
    c = 3
    for time_val in time_list:
        time_name = time_val
        if time_val=='day':
            time_name= time_val + 'per month'
        
        plt.subplot(1,5,c)
        df.groupby(time_val)['sender'].count().plot(kind = 'area',
                                                      title ='Count versus %s' %(time_name) ,color=color[c-1],alpha =a)   
        plt.ylabel('Sent Counts')
        c+=1
    plt.suptitle(name + 'total sent messages for all time increments')
    plt.savefig(name +'_total_sent_messages_for_all_time' +'.png')
    plt.show()

## this will plot times for a sender
# plot_times_sent(enron_df,False,color = ['grey','teal','orange','purple','red'])
## to find all unique contacts of our top ten senders for different times of day.
# I'll have to modify how the data is being grouped and plotted to show unique values
# Since I've grouped and plotted uniquely, there is no better way to approach this than another function.

def plot_all_times_unique_sender(df,name,sender_bool=True, color = ['grey','teal','orange','purple','red']):
    # This function will, based on the recipient name, find all unique senders for all time scales
    reciever_df = df[df['recipients'] == name] 
    time_list =['date','year','month','weekday','day']
    c = 1
    plt.figure(figsize=(30,5))
    for time in time_list:
        time_val=time
        rotate=0
        color_val = color[c-1]
        time_grouped = reciever_df.groupby([time,'sender']).sum().reset_index()
        if time =='year':
            ax = plt.subplot(1,5,c)
            time_grouped.groupby(time)['count'].sum().plot(kind = 'area',
                                                           title='Counts versus year',color=color_val,alpha=1)
            ax.set_xticks(time_grouped.reset_index().year)
            ax.set_xticklabels(time_grouped.reset_index().year)
        else:
            if time =='day':
                time_val ='days per month'
            elif time=='date':
                rotate=80
            ax = plt.subplot(1,5,c)

            time_grouped.groupby(time)['count'].sum().plot(kind = 'area',title="Counts versus %s" % (time_val),
                                                           color=color_val,alpha=1,rot=rotate)
            plt.ylabel('Sent Counts')
            
        c+=1
                
    plt.suptitle(name + ' total unique contants for this top sender')
    plt.savefig(name+'_total_unique_contants_top_sender' +'.png')


def plot_all_top_senders(df=enron_df,unique_sender = True, top_ten = top_ten_sender):
    if unique_sender==True:
        ## this will look at contacts of the top sender and visualize them over time
        for name in top_ten:
             plot_all_times_unique_sender(df,name)
    else:
        #This will look at all the top senders sent out messages over time
        for i in range(0,10):
            person_df = enron_df[enron_df['sender']  == top_ten_sender[i]]
            plot_times_sent(person_df,True)
    

## Plot all for the sender or the senders unique contacts
plot_all_top_senders(enron_df,True,top_ten_sender)
## plot all times for one name
plot_all_top_senders(enron_df,False,top_ten_sender)

print('All Finished Producing Images')
