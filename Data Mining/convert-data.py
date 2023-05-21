import argparse
import itertools
import xml.etree.ElementTree as Xml

#
# Technologies
#

class Tech:
    def __init__(self, ident, name, baseCost):
        self.ident = ident
        self.name = name
        self.baseCost = baseCost
        self.prereqs = []

class TechnologyList:
    def __init__(self):
        self.technologies = {}
    def AddTech(self, tech):
        self.technologies[tech.ident] = tech
    def Iterate(self):
        return self.technologies.values()
    def AddPrereq(self, ident, prereqIdent):
        self.technologies[ident].prereqs.append(prereqIdent)
    def CorrectForAgriculture(self):
        self.technologies["TECH_AGRICULTURE"].baseCost = 0
    def GetCumulativeCost(self, tech, visited):
        if tech.ident in visited:
            return 0
        visited.add(tech.ident)
        total = tech.baseCost
        for prereqIdent in tech.prereqs:
            prereq = self.technologies[prereqIdent]
            total += self.GetCumulativeCost(prereq, visited)
        return total
    def Sorted(self):
        sortedTechs = []
        for tech in self.technologies.values():
            total = self.GetCumulativeCost(tech, set())
            sortedTechs.append((total, tech))
        sortedTechs.sort(key=lambda t: (t[0], t[1].name))
        groupedTechs = []
        for key, group in itertools.groupby(sortedTechs, key=lambda t: t[0]):
            groupedTechs.append((key, list(map(lambda t: t[1], list(group)))))
        return groupedTechs
    def DumpCSV(self, path):
        sortedTechs = self.Sorted()
        with open(path, 'w') as fileHandle:
            for (cumulativeCost, techs) in sortedTechs:
                fileHandle.write(f"{cumulativeCost}, {', '.join([tech.name for tech in techs])}\n")

class TechReader:
    @staticmethod
    def ConvertIdentToName(ident):
        return ident[5:].replace('_', ' ').title()

    @staticmethod
    def Parse(xmlSource):
        xml = Xml.parse(xmlSource)

        techList = TechnologyList()

        xmlTechs = xml.find("Technologies")
        for xmlTech in xmlTechs.iter("Row"):
            ident = xmlTech.find("Type").text
            name = TechReader.ConvertIdentToName(ident)
            baseCost = int(xmlTech.find("Cost").text)

            techList.AddTech(Tech(ident, name, baseCost))

        xmlPrereqs = list(xml.find("Technology_PrereqTechs").iter("Row"))
        for tech in techList.Iterate():
            matchingRows = filter(lambda p: tech.ident == p.find("TechType").text, xmlPrereqs)
            for row in matchingRows:
                techList.AddPrereq(row.find("TechType").text, row.find("PrereqTech").text)

        # Agriculture has a cost of 20 in the game files for some reason,
        # but since we get it automatically, let's set it to a cost of 0
        techList.CorrectForAgriculture()

        return techList

def Main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["Technologies"], required=True)
    parser.add_argument("--to", choices=["csv"], required=True)
    args = parser.parse_args()

    if vars(args)["type"] == "Technologies":
        rep = TechReader.Parse("CIV5Technologies.xml")

    if vars(args)["to"] == "csv":
        rep.DumpCSV("CIV5Technologies.csv")

if __name__ == '__main__':
    Main()
