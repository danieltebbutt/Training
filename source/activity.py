# Activity for Dan's training application.
# This contains all training information for a single activity.
import math

class Activity:

    def __init__(self, date, distance = 0.0, time = 0, notes = "", heartrate = 0, elevation = 0, route = ""):
        self.date = date
        self.distance = distance
        self.time = time
        self.notes = notes
        self.heartrate = heartrate
        self.elevation = elevation
        self.raceName = ""
        self.route = route
        self.tags = []
        if "Treadmill" in self.route:
            self.setTag("TREADMILL")

    def setTag(self, tag):
        self.tags.append(tag)
            
    def tagSet(self, tag):
        return (tag in self.tags)
            
    def toString(self):
        return "%s %.2fkm %s %s %s"%(self.date.strftime("%Y-%b-%d"), self.distance, self.time, self.raceName if self.tagSet("RACE") else "     ", self.notes)

    def toLongString(self):
        return "%s %2.1fkm %s %dbpm fit:%.1f int:%.1f %s"%(self.date.strftime("%Y-%b-%d"), self.distance, self.time, self.heartrate, self.fitness(), self.intensity(), self.notes)

    def isTreadmill(self):
        return self.tagSet("TREADMILL")

    def isRace(self):
        return self.tagSet("RACE")
        
    def intensity(self):
        if self.heartrate != 0:
            return math.pow(1.06, math.log(self.distance, 2)) * (self.heartrate - 80) * (100.0 / 117)
        else:
            return 0
        
    def summaryString(self):
        if self.isRace():
            return "%s %s %s"%(self.date.strftime("%b-%Y"), self.raceName, self.time)
        else:
            return "%s %.2fkm %s"%(self.date.strftime("%Y-%b-%d"), self.distance, self.time)

    def fitScore(self, distance, seconds, heartrate, elevation):
        speed = distance * 3600.0 / seconds
        heartrateAdjust = (175.0 - 80) / (heartrate - 80)
        elevationAdjust = (75.0 * elevation) / (distance * 1000)
        score = speed * heartrateAdjust + elevationAdjust
        return score

    def raceDistance(self):
        if self.distance > 20 and self.distance < 22:
            # HM
            return 21
        elif self.distance > 41 and self.distance < 43:
            # Marathon
            return 42
        elif self.distance > 9 and self.distance < 11:
            # 10k
            return 10
        elif self.distance > 4 and self.distance < 6:
            # 5k
            return 5
        else:
            print "Unrecognized race distance: %.1f"%self.distance
            return 0

    def raceFitness(self):
        # Ignore recorded heartrate and calculate expected based on distance

        heartrates = { 5  : 187.0,
                       10 : 181.0,
                       21 : 175.0,
                       42 : 170.0 }

        heartrate = heartrates[self.raceDistance()]

        return self.fitScore(self.distance, self.time.total_seconds(), heartrate, self.elevation)

    def fitness(self):
        if self.heartrate == 0:
            return 0
        else:
            return self.fitScore(self.distance, self.time.total_seconds(), self.heartrate, self.elevation)

    def setRace(self, name):
        self.setTag("RACE")
        self.raceName = name

