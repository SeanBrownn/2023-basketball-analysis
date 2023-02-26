import requests
import string
import datetime
import numpy as np
from bs4 import BeautifulSoup

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/50.0.2661.102 Safari/537.36'}
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn', disables settingWithCopyWarning
lineupData=pd.DataFrame()
mainPage="https://athletics.case.edu/sports/mbkb/2022-23/schedule"
urls=[]
page = requests.get(mainPage,headers=header)
soup=BeautifulSoup(page.content,"html.parser")
links=soup.findAll('a')
for link in links:
    href=str(link.get('href'))
    if "boxscores" in href and "mbkb" in href:
        urls.append("https://athletics.case.edu"+href)
for url in urls[:10]:
    page = requests.get(url, headers=header)  # change to url once doing loop for each url
    html = page.text
    tables = pd.read_html(html)
    vBoxScore = tables[1]  # visiting team box score
    hBoxScore = tables[2]  # home team box score
    vRoster=vBoxScore.loc[:,'Player']
    vRoster=vRoster[1:len(vRoster)-3]
    vRoster=vRoster.drop(vRoster.index[5]) # vRoster is all players on visiting team
    hRoster=hBoxScore.loc[:,'Player']
    hRoster=hRoster[1:len(hRoster)-3]
    hRoster=hRoster.drop(hRoster.index[5]) #hRoster is all players on home team
    def nameReverse(str,special): # converts starter names into the same format used in the play by play
        if special:
            str=str.replace(","," ")
            x=str.split(" ")
            return x[2].upper()+","+x[3].upper()
        str = str.replace(",", "")
        x=str.split(" ")
        return x[3].upper()+","+x[2].upper()
    if url==urls[8]:
        vRoster=[nameReverse(v,True) for v in vRoster]
    else:
        vRoster=[nameReverse(v,False) for v in vRoster]
    hRoster=[nameReverse(h,False) for h in hRoster]
    if url == urls[1]:
        vRoster = ["GANNON,ANDREW", "RADUSINOVIC,D", "OTASEVIC,DORDE", "OKUBO,YUUKI", "OTLEY,COLE",
                   "LIEBER,HENRY","BOUSQUETTE,WILL","SNIPES-REA,ASAAN","REYNOLDS,JACKSON",
                   "MICANOVIC,MILUN"]
    vStarters = vRoster[:5]  # visiting team starters
    hStarters = hRoster[:5]  # home team starters
    gameInfo = tables[3]
    caseHome = False  # variable says whether Case is the home team
    if "Horsburgh Gym" in gameInfo[1][1]:
        caseHome = True
    def typos(str): # addresses typos
        str=str.replace("LAWSON JR,JESSE","LAWSON,JESSE")
        str=str.replace("BOUSQUETTE III,WILL","BOUSQUETTE,WILL")
        if str=="LAWSON":
            return "LAWSON,JESSE"
        return str
    firstHalfPlays = tables[4][:-1]  # first half play by play
    firstHalfPlays[2] = firstHalfPlays[2].fillna("0 - 0")  # provides score for the plays before a team scored
    firstHalfPlays[['vScore', 'hScore']] = firstHalfPlays[2].str.split(" - ",expand=True)  # adds column for visitor and home score
    secondHalfPlays = tables[5][:-1]  # second half play by play
    secondHalfPlays[2] = secondHalfPlays[2].fillna("0 - 0")
    secondHalfPlays[['vScore', 'hScore']] = secondHalfPlays[2].str.split(" - ", expand=True)
    vEnters = firstHalfPlays.loc[firstHalfPlays[1].str.contains('enters the game',na=False)].T  # all times in the first half when a visiting player enters the game
    vLeaves = firstHalfPlays.loc[firstHalfPlays[1].str.contains('goes to the bench', na=False)].T
    hEnters = firstHalfPlays.loc[firstHalfPlays[3].str.contains('enters the game',na=False)].T  # all times in the first half when a home player enters the game
    hLeaves = firstHalfPlays.loc[firstHalfPlays[3].str.contains('goes to the bench', na=False)].T
    vEnters2 = secondHalfPlays.loc[secondHalfPlays[1].str.contains('enters the game', na=False)]  # second half
    vLeaves2 = secondHalfPlays.loc[secondHalfPlays[1].str.contains('goes to the bench', na=False)]
    hEnters2 = secondHalfPlays.loc[secondHalfPlays[3].str.contains('enters the game', na=False)]  # second half
    hLeaves2 = secondHalfPlays.loc[secondHalfPlays[3].str.contains('goes to the bench', na=False)]
    vE2 = [typos(v)[0:v.index(" ")] for v in vEnters2[1].copy()]  # copy used to preserve vEnters2 for play by play iteration
    vL2 = [typos(v)[0:v.index(" ")] for v in vLeaves2[1].copy()]
    vStarters2 = []
    def fixTypos(arr): # fixes typos for an array
        for i in range(len(arr)):
            arr=[typos(x) for x in arr]
    for i in range(len(vL2)):  # finds visiting team second half starters
        vL2[i] = typos(vL2[i])
        vE2[i] = typos(vE2[i])
        if vL2[i] not in vE2[0:i]:
            vStarters2.append(vL2[i])
    hE2 = [h[0:h.index(" ")] for h in hEnters2[3].copy()]
    hL2 = [h[0:h.index(" ")] for h in hLeaves2[3].copy()]
    hStarters2 = []
    for i in range(len(hL2)):  # finds home team second half starters
        hL2[i] = typos(hL2[i])
        hE2[i] = typos(hE2[i])
        if hL2[i] not in hE2[0:i]:
            hStarters2.append(hL2[i])
    vEnters2 = vEnters2.T
    vLeaves2 = vLeaves2.T
    hEnters2 = hEnters2.T
    hLeaves2 = hLeaves2.T
    def dateTime(str):  # converts times to datetime objects so we can compare them
        arr = str.split(":")
        return datetime.datetime(1, 1, 1, 0, int(arr[0]), int(arr[1]))
    firstHalfPlays[0] = [dateTime(t) for t in firstHalfPlays[0]]
    secondHalfPlays[0] = [dateTime(t) for t in secondHalfPlays[0]]
    if url==urls[0]:
        hStarters2=["RASHID,UMAR", "ELAM,IAN", "THORBURN,LUKE","FRAUENHEIM,DANNY","FRILLING,COLE"]
    if url==urls[3]:
        hStarters2=["ELAM,IAN","FRAUENHEIM,DANNY","FRILLING,COLE","THORBURN,LUKE","RASHID,UMAR"]
    if url==urls[4]:
        secondHalfPlays=secondHalfPlays.iloc[8:] # drops first 8 rows
        hStarters2=["EYINK,ALEX","CRAWFORD,KALEB","COMBS,CARTER","NIXON,JUSTIN","DOSECK,GRIFFIN"]
        vStarters2=["RASHID,UMAR","ELAM,IAN","THORBURN,LUKE","FRILLING,COLE","FRAUENHEIM,DANNY"]
    if url==urls[7]:
        secondHalfPlays=secondHalfPlays.iloc[16:]
        hStarters2=["SANDERS,TRAVIS","SMITH,BRYCE","WILCOTT,DAUNTE","MOULTRIE,COLBY","BILE,JORAREI"]
        vStarters2=["FRILLING,COLE","THORBURN,LUKE","FRAUENHEIM,DANNY","RASHID,UMAR","ELAM,IAN"]
    firstHalfPlays = firstHalfPlays.T
    secondHalfPlays = secondHalfPlays.T
    vQueue = []  # visiting team players waiting to check in
    hQueue = []  # home team players waiting to check in
    caseLineups = []  # list of the different lineups Case uses throughout the game
    oppLineups = []  # list of lineups opponent uses throughout a game
    diffs = []  # point differentials of each lineup Case used
    times = []  # amount of time each lineup was on the floor
    game = []  # which game we are looking at
    poss=[0] # number of possessions a lineup has
    fgm2=[0] # field goals made for a given Case lineup
    fga2=[0] # field goals attempted for a given Case lineup
    fgm3=[0]
    fga3=[0]
    ftm = [0]
    fta = [0]
    oreb=[0]
    dreb=[0]
    tov=[0]
    ast=[0]
    oppPoss=[0]
    oppfgm2=[0] # field goals made for given opponent lineup
    oppfga2=[0]
    oppfgm3=[0]
    oppfga3=[0]
    oppftm=[0]
    oppfta=[0]
    opporeb=[0]
    oppdreb=[0]
    opptov=[0]
    oppast=[0]
    ot = False
    otPlays = tables[6][:-1]
    hStarters3 = []  # ADDRESS IF OVERTIME
    vStarters3 = []
    if len(otPlays.columns) == 4:
        ot = True
        otPlays[['vScore', 'hScore']] = otPlays[2].str.split(" - ",expand=True)  # adds column for visitor and home score
        otPlays[0] = [dateTime(t) for t in otPlays[0]]
        vEnters3 = otPlays.loc[otPlays[1].str.contains('enters the game', na=False)]
        vLeaves3 = otPlays.loc[otPlays[1].str.contains('goes to the bench', na=False)]
        hEnters3 = otPlays.loc[otPlays[3].str.contains('enters the game', na=False)]
        hLeaves3 = otPlays.loc[otPlays[3].str.contains('goes to the bench', na=False)]
        otPlays=otPlays.T
    def isSub(play, vE, vL, hE, hL):
        return (play in vE or play in vL or play in hE or play in hL)  # returns whether a play is a substitution or not
    def updateStats(play,event,casePlay,i,teamWithBall,vE,vL,hE,hL):
        if isSub(play,vE,vL,hE,hL):
            teamWithBall=" "
        elif casePlay:
            if "Foul" not in event and isSub(play,vE,vL,hE,hL)==False and teamWithBall!="Case":
                poss[i]=poss[i]+1
                teamWithBall="Case"
        else:
            if "Foul" not in event and isSub(play,vE,vL,hE,hL)==False and teamWithBall!="opp":
                oppPoss[i]=oppPoss[i]+1
                teamWithBall="opp"
        if "made" in event:
            if "free throw" in event:
                if casePlay:
                    ftm[i]=ftm[i]+1
                    fta[i]=fta[i]+1
                else:
                    oppftm[i]=oppftm[i]+1
                    oppfta[i]=oppfta[i]+1
            elif "3-pt" in event:
                if casePlay:
                    fgm3[i]=fgm3[i]+1
                    fga3[i]=fga3[i]+1
                else:
                    oppfgm3[i]=oppfgm3[i]+1
                    oppfga3[i]=oppfga3[i]+1
            else:
                if casePlay:
                    fgm2[i]=fgm2[i]+1
                    fga2[i]=fga2[i]+1
                else:
                    oppfgm2[i]=oppfgm2[i]+1
                    oppfga2[i]=oppfga2[i]+1
        elif "missed" in event:
            if "free throw" in event:
                if casePlay:
                    fta[i]=fta[i]+1
                else:
                    oppfta[i]=oppfta[i]+1
            elif "3-pt" in event:
                if casePlay:
                    fga3[i]=fga3[i]+1
                else:
                    oppfga3[i]=oppfga3[i]+1
            else:
                if casePlay:
                    fga2[i]=fga2[i]+1
                else:
                    oppfga2[i]=oppfga2[i]+1
        elif "rebound" in event and "deadball" not in event:
            if "offensive" in event:
                if casePlay:
                    oreb[i]=oreb[i]+1
                else:
                    opporeb[i]=opporeb[i]+1
            elif "defensive" in event:
                if casePlay:
                    dreb[i]=dreb[i]+1
                else:
                    oppdreb[i]=oppdreb[i]+1
        elif "Turnover" in event:
            if casePlay:
                tov[i]=tov[i]+1
            else:
                opptov[i]=opptov[i]+1
        elif "Assist" in event:
            if casePlay:
                ast[i]=ast[i]+1
            else:
                oppast[i]=oppast[i]+1
        return teamWithBall
    def iterate(hS, vS, vE, vL, hE, hL, d, plays,statInd,hasBall):
        vLineup = vS.copy()  # current lineup for visiting team
        vLineup=[typos(v) for v in vLineup]
        hLineup = hS.copy()  # current lineup for home team
        hLineup=[typos(h) for h in hLineup]
        if caseHome:
            caseLineups.append(hS.copy())
            oppLineups.append(vS.copy())
        else:
            caseLineups.append(vS.copy())
            oppLineups.append(hS.copy())
        subBefore = False
        lastDiff = d  # point differential when the last lineup left the floor
        if hS == hStarters3:
            lastTime = datetime.datetime(1, 1, 1, 0, 5, 0)  # time when last lineup left the floor
        else:
            lastTime = datetime.datetime(1, 1, 1, 0, 20, 0)
        for p in plays:
            if p in vE:
                player = typos(plays[p][1])
                vLineup.append(player[0:player.index(" ")])
                subBefore = True
            elif p in vL:
                player = typos(plays[p][1])
                vLineup.remove(player[0:player.index(" ")])  # removes the player from current lineup
                subBefore = True
            elif p in hE:
                player = typos(plays[p][3])
                hLineup.append(player[0:player.index(" ")])
                subBefore = True
            elif p in hL:
                player = typos(plays[p][3])
                hLineup.remove(player[0:player.index(" ")])
                subBefore = True
            else:
                if p>0 and subBefore:  # if substitutions have just been made and we are done with them
                    currentTime = plays[p - 1][0]
                    times.append(lastTime - currentTime)
                    lastTime = currentTime
                    if caseHome:
                        diff = int(plays[p - 1]['hScore']) - int(plays[p - 1]['vScore'])
                        if lastDiff != 1000:
                            diffCopy = diff
                            diff -= lastDiff  # finds point differential of current lineup
                            # does current diff minus diff when previous lineup left the floor
                            lastDiff = diffCopy
                        else:
                            lastDiff = diff
                        caseLineups.append(hLineup.copy())  # copy is needed because adding a list only
                        # adds a reference to the list instead of making a copy
                        oppLineups.append(vLineup.copy())
                        diffs.append(diff)
                    else:
                        diff = int(plays[p - 1]['vScore']) - int(plays[p - 1]['hScore'])
                        diffCopy = diff
                        diff -= lastDiff  # finds point differential of current lineup
                        # does current diff minus diff when previous lineup left the floor
                        lastDiff = diffCopy
                        caseLineups.append(vLineup.copy())  # copy is needed because adding a list only
                        # adds a reference to the list instead of making a copy
                        oppLineups.append(hLineup.copy())
                        diffs.append(diff)
                    subBefore = False
                    statInd=statInd+1
                    poss.append(0)
                    fgm2.append(0)
                    fga2.append(0)
                    fgm3.append(0)
                    fga3.append(0)
                    ftm.append(0)
                    fta.append(0)
                    oreb.append(0)
                    dreb.append(0)
                    tov.append(0)
                    ast.append(0)
                    oppPoss.append(0)
                    oppfgm2.append(0)
                    oppfga2.append(0)
                    oppfgm3.append(0)
                    oppfga3.append(0)
                    oppftm.append(0)
                    oppfta.append(0)
                    opporeb.append(0)
                    oppdreb.append(0)
                    opptov.append(0)
                    oppast.append(0)
            if plays[p][1]==plays[p][1]: # if play is for away team
                if caseHome:
                    hasBall=updateStats(p,plays[p][1],False,statInd,hasBall,vE,vL,hE,hL)
                else:
                    hasBall=updateStats(p,plays[p][1], True,statInd,hasBall,vE,vL,hE,hL)
            elif plays[p][3]==plays[p][3]: # home team play
                if caseHome:
                    hasBall=updateStats(p,plays[p][3],True,statInd,hasBall,vE,vL,hE,hL)
                else:
                    hasBall=updateStats(p,plays[p][3],False,statInd,hasBall,vE,vL,hE,hL)
        lastPlay = len(plays.axes[1]) - 1
        times.append(lastTime - datetime.datetime(1, 1, 1, 0, 0, 0))  # adds time of lineup that played until halftime
        if caseHome:  # adds diff of lineup that played until end of half
            diff = int(plays[lastPlay]['hScore']) - int(plays[lastPlay]['vScore'])
            diff -= lastDiff
            diffs.append(diff)
        else:
            diff = int(plays[lastPlay]['vScore']) - int(plays[lastPlay]['hScore'])
            diff -= lastDiff
            diffs.append(diff)
    iterate(hStarters, vStarters, vEnters, vLeaves, hEnters, hLeaves, 0, firstHalfPlays,0," ")
    poss.append(0)
    fgm2.append(0)
    fga2.append(0)
    fgm3.append(0)
    fga3.append(0)
    ftm.append(0)
    fta.append(0)
    oreb.append(0)
    dreb.append(0)
    tov.append(0)
    ast.append(0)
    oppPoss.append(0)
    oppfgm2.append(0)
    oppfga2.append(0)
    oppfgm3.append(0)
    oppfga3.append(0)
    oppftm.append(0)
    oppfta.append(0)
    opporeb.append(0)
    oppdreb.append(0)
    opptov.append(0)
    oppast.append(0)
    iterate(hStarters2, vStarters2, vEnters2, vLeaves2, hEnters2, hLeaves2, sum(diffs),
            secondHalfPlays,len(fgm2)-1," ")
    if ot==True:
        iterate(hStarters3,vStarters3,vEnters3,vLeaves3,hEnters3,hLeaves3,sum(diffs),otPlays,0)
    data={'game':url[57:65],'Case lineup':caseLineups,'opponent lineup':oppLineups,'diff':diffs,
          'possessions':poss,'time':times,'2-PT FGM':fgm2,'2-PT FGA':fga2, '3-PT FGM':fgm3,'3-PT FGA':fga3,
          'FTM':ftm, 'FTA':fta, 'OREB':oreb, 'DREB':dreb, 'TOV':tov, 'AST':ast,
          'opp possessions':oppPoss, 'opp 2-PT FGM':oppfgm2, 'opp 2-PT FGA':oppfga2, 'opp 3-PT FGM':oppfgm3,
          'opp 3-PT FGA':oppfga3, 'opp FTM':oppftm, 'opp FTA':oppfta, 'opp OREB':opporeb,
          'opp DREB':oppdreb, 'opp TOV':opptov, 'opp AST':oppast}
    lData=pd.DataFrame(data)
    lData['OREB%']=(lData['OREB']/(lData['OREB']+lData['opp DREB']))
    lData['opp OREB%']=(lData['opp OREB']/(lData['opp OREB']+lData['DREB']))
    move=lData.pop("OREB%")
    lData.insert(13,"OREB%",move)
    lData['eFG%']=((lData['2-PT FGM']+1.5*lData['3-PT FGM'])/(lData['2-PT FGA']+lData['3-PT FGA']))
    move=lData.pop("eFG%")
    lData.insert(9,"eFG%",move)
    lData['opp eFG%'] =((lData['opp 2-PT FGM'] + 1.5*lData['opp 3-PT FGM']) /
                        (lData['opp 2-PT FGA'] + lData['opp 3-PT FGA']))
    move=lData.pop("opp eFG%")
    lData.insert(19, "opp eFG%",move)
    lData['FT rate']=(lData['FTM']/(lData['2-PT FGA']+lData['3-PT FGA']))
    move=lData.pop("FT rate")
    lData.insert(12,"FT rate", move)
    lData['opp FT rate']=(lData['opp FTM']/(lData['opp 2-PT FGA']+lData['opp 3-PT FGA']))
    move=lData.pop("opp FT rate")
    lData.insert(23,"opp FT rate", move)
    lData['TOV%']=(lData['TOV']/lData['possessions'])
    lData['opp TOV%']=(lData['opp TOV']/lData['opp possessions'])
    lData['points/poss']=((2*lData['2-PT FGM']+3*lData['3-PT FGM']+lData['FTM'])/lData['possessions'])
    lData['opp points/poss'] = ((2 * lData['opp 2-PT FGM'] + 3 * lData['opp 3-PT FGM'] +
                                 lData['opp FTM']) / lData['opp possessions'])
    lData['points'] = (lData['possessions'] * lData['points/poss'])
    lData['opp points']=(lData['opp possessions'] * lData['opp points/poss'])
    lData['AST%']=(lData['AST']/(lData['2-PT FGM']+lData['3-PT FGM']))
    lData['opp AST%'] = (lData['opp AST'] / (lData['opp 2-PT FGM'] + lData['opp 3-PT FGM']))
    lineupData=pd.concat([lineupData,lData],axis=0)
print(lineupData.to_string())