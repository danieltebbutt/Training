# Perio for Dan's training application.
# This contains all training information for a period of time.

from activity import Activity
from datetime import date
from datetime import timedelta

class Period:

    def __init__(self, startDate = None):
        self.training = []
        self.startDate = startDate
        self.dateList = {}

    def addActivity(self, newActivity):
        # Some clashing data before this date, but afterwards there are some days with >1 run
        if newActivity.date in self.dateList and newActivity.date < date(2015, 1, 1):
            self.removeActivity(self.dateList[newActivity.date])
            print "Removing date %s"%newActivity.date

        self.training.append(newActivity)
        if self.startDate == None or self.startDate > newActivity.date:
            self.startDate = newActivity.date

        # If there's a clash then decide which to store based on pace
	if not newActivity.date in self.dateList or \
           self.dateList[newActivity.date].pace() > newActivity.pace():
            self.dateList[newActivity.date] = newActivity

    def registerRace(self, date, name):
        if not date in self.dateList:
            print "Unable to register race: %s %s %s"%(date, name, self.dateList)
            return

        self.dateList[date].setRace(name)

    def containsRace(self):
        for activity in self.training:
            if activity.tagSet("RACE"):
               return True
        return False

    def getRaces(self):
        return self.filter("RACE").training

    def filter(self, tag):
        newPeriod = Period()
        for activity in self.sorted():
            if activity.tagSet(tag):
                newPeriod.addActivity(activity)
        return newPeriod
        
    def getTreadmillPeriod(self):
        return self.filter("TREADMILL")

    def removeActivity(self, activity):
        self.training.remove(activity)
        del self.dateList[activity.date]

    def dump(self):
        for activity in self.sorted():
            print activity.toLongString()

    def clash(self, comparison):
        for item in comparison.training:
            if item.date in self.dateList:
                return True
        return False

    def sorted(self):
        return sorted(self.training, key=lambda act: act.date)

    def getWeeks(self):
        weeks = []
        startDate = None
        thisWeek = None
        for activity in self.sorted():
            if startDate == None:
                startDate = activity.date
                startDate -= timedelta(days = startDate.weekday())
                thisWeek = Period()

            # Fill in any weeks with no running; start new week if required
            while activity.date >= startDate + timedelta(days = 7):
                weeks.append(thisWeek)
                startDate = startDate + timedelta(days = 7)
                thisWeek = Period(startDate)

            # Now thisWeek should exist and be the right one to use
            thisWeek.addActivity(activity)

        weeks.append(thisWeek)
        return weeks

    def getMonths(self):
        months = []
        startDate = None
        thisMonth = None
        for activity in self.sorted():
            if startDate == None:
                startDate = activity.date.replace(day=1)
                thisMonth = Period()

            # Fill in any months with no running; start new week if required
            while (activity.date.year, activity.date.month) != (startDate.year, startDate.month):                
                months.append(thisMonth)
                if startDate.month == 12:
                    startDate = startDate.replace(year = startDate.year+1, month = 1)
                else:
                    startDate = startDate.replace(month = startDate.month+1)
                thisMonth = Period(startDate)

            # Now thisWeek should exist and be the right one to use
            thisMonth.addActivity(activity)

        months.append(thisMonth)
        return months

    def getYears(self):
        years = []
        startDate = None
        thisYear = None
        for activity in self.sorted():
            if startDate == None:
                startDate = activity.date.replace(day=1, month=1)
                thisYear = Period()

            # Fill in any months with no running; start new week if required
            while activity.date.year != startDate.year:                
                years.append(thisYear)
                startDate = startDate.replace(year = startDate.year+1)
                thisYear = Period(startDate)

            # Now thisWeek should exist and be the right one to use
            thisYear.addActivity(activity)

        years.append(thisYear)
        return years

    def getFitness(self):
        fitness = []

        for activity in self.sorted():
            if activity.fitness() != 0:
                fitness.append(activity)

        return fitness

    def kilometres(self):
        distance = 0.0
        for activity in self.training:
            distance += activity.distance
        return distance

    def time(self):
        totalTime = timedelta(hours = 0)
        for activity in self.training:
            totalTime += activity.time
        return totalTime

    def heartbeats(self):
        heartbeats = 0
        timeMeasured = timedelta(seconds = 0)
        for activity in self.training:
            if activity.heartrate > 0:
                heartbeats += activity.heartrate * activity.time.total_seconds() / 60
                timeMeasured += activity.time
        return (heartbeats, timeMeasured)

    def longest(self):
        longest = timedelta(seconds = 0)
        for activity in self.training:
            longest = max(longest, activity.time)
        return longest

    def furthest(self):
        furthest = 0
        for activity in self.training:
            furthest = max(furthest, activity.distance)
        return furthest

    def highestHR(self):
        heartrate = 0
        for activity in self.training:
            heartrate = max(heartrate, activity.heartrate)
        return heartrate
    
    def longestStreak(self):
        longest = 0
        datelist = [ activity.date for activity in self.training ]
        datelist.sort()
        streak = 1
        lastdate = date(2000, 1, 1)
        for rundate in datelist:
            print "%s %d %d"%(rundate, longest, streak)
            if (rundate - lastdate).days == 1:
                streak = streak + 1
            elif (rundate - lastdate).days > 1:
                streak = 1
            if streak > longest:
                longest = streak
            lastdate = rundate
        return longest
    
    def bestActivity(self, distance):
        bestTime = timedelta(seconds = 60 * 60 * 24)
        for activity in self.training:
            if activity.distance >= distance and \
               activity.time < bestTime:
                bestTime = activity.time 
                bestActivity = activity       
        return bestActivity

    def bestTime(self, distance):
        return self.bestActivity(distance).time
       
    def bestDescription(self, distance):
        return "%s"%self.bestActivity(distance).raceDate()
 
    def range(self, startDate, endDate = None):
        myRange = Period()

        for activity in self.training:
            if activity.date >= startDate and      \
                    (endDate == None or activity.date <= endDate):
                myRange.addActivity(activity)

        return myRange

