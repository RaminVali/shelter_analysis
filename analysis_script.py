'''Script for analysis and plotting of Toronto Homeless Shelter Usage Data
Submitted by Ramin Vali as part of Homework1 for Building Software Module
of the DSI course'''

'''Variables chose: group by (commandline), link to the dataset (user level), plot_style (job level)'''

import pandas as pd
import matplotlib.pylab as plt
import matplotlib.ticker as tick

import argparse
import yaml

## Loading ##
def load_data(config):
    '''The link to the dataset is one of the varibales we can put into user config'''
    df = pd.read_csv(config['dataset_url'])# job config variable
    return df

## Preprocessing ##
def null_col_drop(df, pct = 0.35):
    '''Drop columns with more then 35% missing values, then drop any row with missing values'''
    drop_mask = (df.isnull().sum()/df.shape[0])<pct # making a mask for columns with a percentage missing value rate higher than 35%
    cols_to_keep = [c for c in df.columns if drop_mask[c] == True]
    df = df[cols_to_keep].copy()
    df.dropna(axis=0, inplace=True)
    return df

def preprocess(df):
    '''Change column names to lower case and drop nulls and set the datetime column'''
    df['OCCUPANCY_DATE'] = pd.to_datetime(df['OCCUPANCY_DATE']) # Get date time object
    df = df.rename(columns=str.lower) # rename columns to lower case
    df = null_col_drop(df, pct = 0.35)
    return df

## Analysis ##
def analysis_and_plot(df, config):
    '''Perform analysis based on the column to groupby and call the appropriate plotting functions'''

    if config['group_col'] == 'occupancy_date': # group_col is a commandline variable here, 3 choices
        grouped = (df.groupby('occupancy_date')
                   .agg(total_capacity = ('capacity_actual_bed', 'sum'),
                    sum_occu_beds = ('occupied_beds', 'sum'),
                    sum_unoccu_beds = ('unoccupied_beds', 'sum')))
        utilisation_plot(grouped, config)
    
    elif config['group_col'] == 'sector':
        grouped = df.groupby(['sector'])['occupied_beds'].sum()/365
        bar_plot(grouped,config)

    elif config['group_col'] == 'both':
        grouped = df.groupby(['occupancy_date','sector'])\
                                     ['service_user_count'].sum().reset_index()
        sector_utility_plot(grouped,config)
        sector_boxplot(grouped)
    else:
        print('INVALID CHOICE!') 

## Plotting ##

def bar_plot(data, config):
    '''Bar plot for sector grouped data'''
    fig, ax = plt.subplots()
    ax.barh(data.index, data, height=.3, color=config['plot_color']) # job configuration variable
    ax.set_title('Mean Occupied Beds Per Sector')
    ax.xaxis.set_major_formatter(tick.StrMethodFormatter('{x:,.0f}'))
    ax.set_xlabel('Yearly Occupied Beds')
    plt.savefig('Mean_Occupied_Beds_Per_Sector.png')

def utilisation_plot(data, config):
    '''Utilisation plot for grouping by occupancy date only'''
    fig, ax = plt.subplots()
    plt.style.use(config['plot_style']) # user_configuration variable
    ax.plot(data.index, data.total_capacity, label = 'Total Capacity')
    ax.plot(data.index, data.sum_occu_beds, label = 'Occupied Beds')
    ax.plot(data.index, data.sum_unoccu_beds, label = 'Unoccupied Beds')
    ax.set_title('Shelter Bed Capacity and Utilisation for 2023')
    ax.set_ylabel('Number of Beds')
    plt.setp(plt.xticks()[1], rotation=30)
    ax.legend()
    ax.grid(alpha=0.3)
    plt.savefig('Shelter_Bed_Capacity_Utilisation_2023')

def sector_utility_plot(data,config):
    '''Sector utility plot used when both sector and occupancy date are passed'''
    fig, ax = plt.subplots(figsize = (8,5))
    plt.style.use(config['plot_style'])# user_configuration variable
    for key, segment in data.groupby('sector'):
        segment.plot(x='occupancy_date', y='service_user_count', ax=ax, label=key)
    ax.set_title('Shelter Bed Usage per Sector per Day')
    ax.set_ylabel('Number of Users')
    plt.setp(plt.xticks()[1], rotation=30)
    ax.legend(bbox_to_anchor=(1, 1),
            loc='upper left')
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('Shelter_Bed_Usage_Sector_Day')

def sector_boxplot(data):
    '''Boxlot per sector used when both sector and occupancy date are passed'''
    boxplot = data.boxplot(by = 'sector', return_type='axes') # using user_per_sector prepared above, returns axes so we can modify
    boxplot.iloc[0].figure.suptitle('Bed User Count Grouped By Sector')
    boxplot.iloc[0].set_title('') # axes title is not needed as we have figsuptile 
    boxplot.iloc[0].set_xlabel('Sectors')
    boxplot.iloc[0].set_ylabel('User Count')
    plt.savefig('Bed_User_Count_Grouped_By_Sector')

def main(config):
    df = load_data(config)
    prepped_df = preprocess(df) 
    analysis_and_plot (prepped_df,config)

# running as script
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Shelter Dataset Analysis Script')
    parser.add_argument('user_config',
                        type=str,
                        help='Path to the user configuration file')
    parser.add_argument('job_config',
                        type=str, 
                        help='Path to the job configuration file')
    parser.add_argument('group_col', 
                        help = 'Group by occupancy_date, sector or both',
                        choices=['occupancy_date', 'sector','both'])
    args = parser.parse_args()


    config_paths = []
    config_paths.extend([args.user_config, args.job_config])
    config = {}
    for path in config_paths:
        with open(path, 'r') as f:
            this_config = yaml.safe_load(f)
            config.update(this_config)

    config.update({'group_col':args.group_col})
    print(config)
    main(config)

