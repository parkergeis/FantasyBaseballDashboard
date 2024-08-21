# MLB Import
from espn_api.baseball import League
import espn_api
import pandas as pd
import warnings
import datetime
import os
today = datetime.date.today()
year = today.year
warnings.filterwarnings('ignore')
pd.set_option("display.max_columns", None)
pd.set_option('display.max_colwidth', None)

# Initializing league
league = League(league_id=929702235, year=2024, swid='5479be06-0e9f-49de-b677-cf8a388a3723', espn_s2='AECG5emtArOlIVusvFSalUmzw1PS5YdPit0EsHfFjMqmVKWmypzFMZ25NYOZ4FDUtj%2B7bVL2s55sZzJW8D7eEoFP4mFWRX9dA65s4DqbT7uKfX%2B7ld5AWgf7pM9qrbVU3PUNnt%2BCb2Aqmwqc%2BiZj8SD5xXAVXXBQuAY5UN6i%2B%2BeMT%2BgfGM3MFI7v2zH7cd85%2BOos82rHMD34i9LUkMpJTftCpsRMwgrG9MZyvxKTSahcI4X7t2%2BJjfcFaD9z7hyastRCz2xBpWvtSVbxNNgyXxbn')

# Previous week
last_full_week = league.currentMatchupPeriod

all_stats = []  # To store all stats for each week

for j in range(last_full_week):
    box = league.box_scores(j + 1)
    for i in range(6):
        # Get home team stats
        home_team = box[i].home_team
        home_stats = pd.DataFrame.from_dict(box[i].home_stats)
        home_stats.insert(0, 'Team', box[i].home_team)
        home_stats.insert(1, 'Opponent', box[i].away_team)
        
        # Get away team stats
        away_team = box[i].away_team
        away_stats = pd.DataFrame.from_dict(box[i].away_stats)
        away_stats.insert(0, 'Team', box[i].away_team)
        away_stats.insert(1, 'Opponent', box[i].home_team)
        
        # Concatenate home and away stats
        df = pd.concat([home_stats, away_stats], ignore_index=False)
        
        # Clean the team names
        df['Opponent'] = df['Opponent'].astype(str)
        df['Team'] = df['Team'].astype(str)
        df['Opponent'] = df['Opponent'].str.replace('Team(', '', regex=False).str.replace(')', '', regex=False)
        df['Team'] = df['Team'].str.replace('Team(', '', regex=False).str.replace(')', '', regex=False)
        
        # Add week information
        df.insert(0, 'Week', j + 1)
        
        # Append to the list
        all_stats.append(df)

# Combine all stats into a single DataFrame
WeeklyData = pd.concat(all_stats, ignore_index=False)

# Assuming 'value' and 'result' columns need to be separated as shown before
stats = WeeklyData.loc['value']
results = WeeklyData.loc['result'].dropna(axis=1)

# Reset indexes
stats.reset_index(drop=True, inplace=True)
results.reset_index(drop=True, inplace=True)

# Combining results and stats

WeeklyData = results
WeeklyData.insert(3, 'HR_val', stats['HR'])
WeeklyData.insert(5, 'WHIP_val', stats['WHIP'])
WeeklyData.insert(7, 'ERA_val', stats['ERA'])
WeeklyData.insert(9, 'K_val', stats['K'])
WeeklyData.insert(11, 'OBP_val', stats['OBP'])
WeeklyData.insert(13, 'SVHD_val', stats['SV']+stats['HLD'])
WeeklyData.insert(15, 'R_val', stats['R'])
WeeklyData.insert(17, 'RBI_val', stats['RBI'])
WeeklyData.insert(19, 'W_val', stats['W'])
WeeklyData.insert(21, 'SB_val', stats['SB'])
WeeklyData['Record'] = WeeklyData.apply(lambda row: (row == 'WIN').sum(), axis=1).astype(str) + '-' + (WeeklyData.apply(lambda row: (row == 'LOSS').sum(), axis=1)).astype(str) + '-' + (WeeklyData.apply(lambda row: (row == 'TIE').sum(), axis=1)).astype(str)
WeeklyData['Points'] = WeeklyData.apply(lambda row: (row == 'WIN').sum(), axis=1) + (WeeklyData.apply(lambda row: (row == 'TIE').sum(), axis=1) * 0.5)

# Gather standings, ranks, rosters up to current day
history = []
rosters = []
records = []
for i in range(2021, year+1):
    # Initialize each year of league
    league = League(league_id=929702235, year=i, swid='5479be06-0e9f-49de-b677-cf8a388a3723', espn_s2='AECG5emtArOlIVusvFSalUmzw1PS5YdPit0EsHfFjMqmVKWmypzFMZ25NYOZ4FDUtj%2B7bVL2s55sZzJW8D7eEoFP4mFWRX9dA65s4DqbT7uKfX%2B7ld5AWgf7pM9qrbVU3PUNnt%2BCb2Aqmwqc%2BiZj8SD5xXAVXXBQuAY5UN6i%2B%2BeMT%2BgfGM3MFI7v2zH7cd85%2BOos82rHMD34i9LUkMpJTftCpsRMwgrG9MZyvxKTSahcI4X7t2%2BJjfcFaD9z7hyastRCz2xBpWvtSVbxNNgyXxbn')
    # Gather historical information
    standings = league.standings()
    df = pd.DataFrame(standings)
    df.rename(columns={0: "Team"}, inplace=True)
    df['Team'] = df['Team'].astype('str')
    df['Team'] = df['Team'].str.replace('Team(', '', regex=False).str.replace(')', '', regex=False)
    df['Rank'] = range(1,len(league.teams)+1)
    df['Year'] = i
    # Assign free agent list to rosters tab
    free_agents = pd.DataFrame(league.free_agents())
    free_agents['Team'] = 'Free Agent'
    free_agents['Owner'] = 'None'
    free_agents['Year'] = i
    free_agents.rename(columns={0: "Player"}, inplace=True)
    free_agents['Player'] = free_agents['Player'].astype('str')
    free_agents['Player'] = free_agents['Player'].str.replace('Player(', '', regex=False).str.replace(')', '', regex=False)
    rosters.append(free_agents)
    # Iterate each team's roster and record
    for j in range(0, len(league.teams)):
        team = league.teams[j]
        df2 = pd.DataFrame(team.roster)
        df2['Year'] = i
        df2['Team'] = team.team_name
        df2['Owner'] = team.owners[0]['firstName'] + " " + team.owners[0]['lastName']
        df2.rename(columns={0: "Player"}, inplace=True)
        df2['Player'] = df2['Player'].astype('str')
        df2['Player'] = df2['Player'].str.replace('Player(', '', regex=False).str.replace(')', '', regex=False)
        rosters.append(df2)

        team = league.teams[j]
        temp = pd.DataFrame({
            'Year': [i],
            'Wins': [team.wins],
            'Losses': [team.losses],
            'Ties': [team.ties],
            'Team': [team.team_name],
            'Owner': [team.owners[0]['firstName'] + " " + team.owners[0]['lastName']]
        }, index=[0])  # Specify an index
        records.append(temp)
        
    history.append(df)


temp1 = pd.concat(history, ignore_index=True)
temp2 = pd.concat(records, ignore_index=True)
PreviousStandings = pd.merge(temp1, temp2, on=['Team', 'Year'])
PreviousStandings['Points'] = PreviousStandings['Wins'] + (0.5*PreviousStandings['Ties'])
Rosters = pd.concat(rosters, ignore_index=True)

# Add bonuses df/tab
def count_wins(series):
    return (series == 'WIN').sum()

max_week = WeeklyData['Week'].max()
Bonuses = WeeklyData[WeeklyData['Week'] != max_week]
# First, find the maximum points for each week
max_points_per_week = Bonuses.groupby('Week')['Points'].max()

# Create a boolean mask for rows where 'Points' is the maximum for the 'Week'
mask = Bonuses.groupby('Week')['Points'].transform(max) == Bonuses['Points']

# Apply the mask to the DataFrame to get only the rows with the maximum 'Points' for each 'Week'
WeeklyWinners_max = Bonuses[mask]

# Then, count the number of times the maximum points occur for each week
counts = WeeklyWinners_max.groupby('Week').size()

# Create a new column 'Prize' and initialize it with $5
WeeklyWinners_max['Prize'] = 5

# Find the weeks where the maximum points occur more than once
weeks_with_multiple_max = counts[counts > 1].index

# For these weeks, set the 'Prize' to 0
WeeklyWinners_max.loc[WeeklyWinners_max['Week'].isin(weeks_with_multiple_max), 'Prize'] = 0

# Create a new column 'Rollover' and initialize it with 0
WeeklyWinners_max['Rollover'] = 0

# For weeks after a week with multiple max, add the rollover amount
rollover = 0
for week in sorted(WeeklyWinners_max['Week'].unique()):
    if week in weeks_with_multiple_max:
        rollover += 5
    else:
        WeeklyWinners_max.loc[WeeklyWinners_max['Week'] == week, 'Rollover'] = rollover
        rollover = 0

# Add the 'Rollover' to the 'Prize'
WeeklyWinners_max['Prize'] += WeeklyWinners_max['Rollover']

# Drop the 'Rollover' column as it's no longer needed
WeeklyWinners_max = WeeklyWinners_max.drop(columns='Rollover')

WeeklyWinners = WeeklyWinners_max[['Week', 'Team', 'Record', 'Prize']]
WeeklyWinners.columns = ['Week', 'Team', 'Record', '$']

TotalPrizes_test = WeeklyWinners[['Team', '$']]
TotalPrizes = TotalPrizes_test.groupby(by='Team').sum()
TotalPrizes['Wins'] = TotalPrizes_test.groupby(by='Team').count()
TotalPrizes.sort_values(by=['$', 'Wins'], ascending=False,inplace=True)
TotalPrizes.reset_index(inplace=True, col_level=0, col_fill='Team')

# Export to SharePoint (for Power BI)
os.chdir('/Users/parkergeis/Library/CloudStorage/OneDrive-WesternGovernorsUniversity/Apps/Microsoft Power Query/Uploaded Files')
with pd.ExcelWriter('FantasyData.xlsx') as writer:  
    WeeklyData.to_excel(writer, sheet_name='WeeklyData', index=False)
    PreviousStandings.to_excel(writer, sheet_name='PreviousStandings', index=False)
    Rosters.to_excel(writer, sheet_name='Rosters', index=False)
    TotalPrizes.to_excel(writer, sheet_name='TotalPrizes', index=False)

# Export locally (for Streamlit)
os.chdir('/Users/parkergeis/Personal/SportsStats/FantasyBaseballApp/data')
with pd.ExcelWriter('FantasyData.xlsx') as writer:  
    WeeklyData.to_excel(writer, sheet_name='WeeklyData', index=False)
    PreviousStandings.to_excel(writer, sheet_name='PreviousStandings', index=False)
    Rosters.to_excel(writer, sheet_name='Rosters', index=False)
    TotalPrizes.to_excel(writer, sheet_name='TotalPrizes', index=False)

# Export to Google (for Tableau)
import gspread
gc = gspread.service_account(filename='/Users/parkergeis/.config/gspread/seismic-bucksaw-427616-e6-5a5f28a2bafc.json')
sh = gc.open("FantasyData")
worksheet1 = sh.worksheet("WeeklyData")
worksheet1.clear()  # Clear the existing content
worksheet1.update([WeeklyData.columns.values.tolist()] + WeeklyData.values.tolist())
worksheet2 = sh.worksheet("PreviousStandings")
worksheet2.clear()  # Clear the existing content
worksheet2.update([PreviousStandings.columns.values.tolist()] + PreviousStandings.values.tolist())
worksheet3 = sh.worksheet("Rosters")
worksheet3.clear()  # Clear the existing content
worksheet3.update([Rosters.columns.values.tolist()] + Rosters.values.tolist())
worksheet4 = sh.worksheet("TotalPrizes")
worksheet4.clear()  # Clear the existing content
worksheet4.update([TotalPrizes.columns.values.tolist()] + TotalPrizes.values.tolist())
