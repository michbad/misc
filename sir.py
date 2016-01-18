# Michal Badura
# "Semantic informational retrieval"
# Builds a simple network of objects and relations
# Inspired by http://dspace.mit.edu/handle/1721.1/6904
import re

rels = []
things = {}
def getThing(name):
    if name not in things:
        Object(name)
    return things[name]


class Relation():
    def __init__(self, leftobj, verb, rightobj, negation=False):
        self.leftobj = leftobj
        self.verb = verb
        self.rightobj = rightobj
        self.negation = negation


    def show(self):
        if self.negation == True:
            if self.verb == "is":
                 printverb = "is not"
            else:
                printverb = "doesn't " + self.verb
        else:
            printverb = self.verb
        return "{0} {1} {2}".format(self.leftobj.name, printverb, self.rightobj.name)


class Object():
    def __init__(self, name, group=None):
        self.name = name
        self.relations = []
        global things
        things[name] = self
        self.group = group

class Group():
    def __init__(self, name):
        self.name = name
        self.all = Object("every {0}".format(name), self)
        self.some = Object("a {0}".format(name), self)
        global things
        things[name] = self

def classify(obj):
    if obj.group==None:
        return "thing"
    elif obj.group.all == obj:
        return "every"
    elif obj.group.some == obj:
        return "exists"

def compare(rel1, rel2):
    if rel1.leftobj == rel2.leftobj and rel1.verb == rel2.verb and rel1.rightobj == rel2.rightobj:
        if rel1.negation == rel2.negation:
            return 1
        else:
            return -1
    else:
        return 0


def parseSentence(text):
    lexp = "(?P<lexp>(a|an|every|not every|no|)\s*([a-zA-Z]+))"
    rexp = "(?P<rexp>(a|an|every|)\s*([a-zA-Z]+))"
    verb_exp = "(?P<verb>((doesn't|)\s*[a-zA-Z]*\s*)|(isn't))"
    general = "{0} {1} {2}".format(lexp, verb_exp, rexp)
    pattern = re.compile(general)
    matches = pattern.match(text)
    matchdict = matches.groupdict()

    leftname, leftneg = parseName(matchdict["lexp"])
    rightname, rightneg = parseName(matchdict["rexp"])
    verbname, verbneg = parseVerb(matchdict["verb"])
    negation = leftneg ^ verbneg

    
    return Relation(leftname, verbname, rightname, negation)

def parseVerb(text):
    if "isn't" not in text and "doesn't" not in text:
        return text, False
    elif text == "isn't":
        return "is", True
    else:
        return text.split()[1]+"s", True


def parseName(text): #takes a thing name, returns an object
    negation = False
    exp = "(?P<article>(a|an|every|not every|no|))\s*(?P<name>([a-zA-Z]+))"
    pattern = re.compile(exp)
    matchdict = pattern.match(text).groupdict()
    article, name = matchdict["article"], matchdict["name"]
    if article == "":
        obj = getThing(name)
    else:
        if name not in things:
            Group(name)
        
        if article in ["a", "an"]:
            obj = getThing(name).some
        elif article == "every":
            obj = getThing(name).all
        elif article == "not every":
            obj = getThing(name).some
            negation = True
        elif article == "no":
            obj = getThing(name).all
            negation = True
    return obj, negation



def addFact(rel):
    leftobj = rel.leftobj
    rightobj = rel.rightobj
    leftobj.relations.append(rel)
    if rel.verb == "is":
        reflexed = Relation(rightobj, "is", leftobj)
        rightobj.relations.append(reflexed)
    global rels
    rels.append(rel)


def addFactFromSentence(text):
    addFact(parseSentence(text))


results = []
def pathsHelper(relChecked, stack = [], visited=[], negated=False):
    leftobj = relChecked.leftobj
    rightobj = relChecked.rightobj
    verb = relChecked.verb
    negated = negated ^ relChecked.negation

    if rightobj == leftobj and verb=="is":
        results.append((stack, negated))

    if classify(leftobj)=="exists":
        pathsHelper(Relation(leftobj.group.all, verb, rightobj), stack, visited+[leftobj], negated)

    for relation in leftobj.relations:
        if relation.leftobj in visited:
            continue

        if compare(relation, relChecked) != 0:
            results.append((stack+[relation], negated^relation.negation))

        if classify(relation.rightobj) == "exists":
            if relation.verb == verb:
                newRelation = Relation(relation.rightobj.group.all, "is", rightobj, relation.negation)
                pathsHelper(newRelation, stack+[relation], visited+[leftobj], negated)
            elif relation.verb == "is" and not relation.negation:
                newRelation = Relation(relation.rightobj.group.all, verb, rightobj, relation.negation)
                pathsHelper(newRelation, stack+[relation], visited+[leftobj], negated)

        elif classify(relation.rightobj) == "every":
            if relation.verb == verb:
                newRelation = Relation(relation.rightobj.group.some, "is", rightobj, relation.negation)
                pathsHelper(newRelation, stack+[relation], visited+[leftobj], negated)
            elif relation.verb == "is" and not relation.negation:
                newRelation = Relation(relation.rightobj.group.some, verb, rightobj)
                pathsHelper(newRelation, stack+[relation], visited+[leftobj], negated)

        else:
            if relation.verb == verb:
                newRelation = Relation(relation.rightobj, "is", rightobj, relation.negation)
                pathsHelper(newRelation, stack+[relation], visited+[leftobj], negated)
            elif relation.verb == "is" and not relation.negation:
                newRelation = Relation(relation.rightobj, verb, rightobj, relation.negation)
                pathsHelper(newRelation, stack+[relation], visited+[leftobj], negated)

def getPaths(relChecked):
    global results
    results = []
    pathsHelper(relChecked)
    return results
    

def showPath(path):
    print([p.show() for p in path])

def check(rel):
    paths = []
    if classify(rel.leftobj) == "every":
        converted = Relation(rel.leftobj.group.some, rel.verb, rel.rightobj, not rel.negation)
        if any([path[1]==False for path in getPaths(converted)]):
            return -1

    paths = getPaths(rel)
    
    if len(paths)==0:
        return 0
    else:
        if classify(rel.leftobj) == "exists":
            if any([path[1]==False for path in paths]):
                return True

        if all([path[1]==True for path in paths]):
            return -1
        elif all([path[1]==False for path in paths]):
            return 1
        else:
            print("WARNING: contradictory information")
            return 0

def respond(inp):
    if inp[-1] == "?":
        text = inp[:-1]
        result = check(parseSentence(text))
        if result==1:
            return "    Yes"
        elif result==-1:
            return "    No"
        else:
            return "    Not sure"
    else:
        addFactFromSentence(inp)
        return "    I understand"


def mainLoop():
    inp = input(": ")
    while True:
        if inp=="exit":
            return
        else:
            print(respond(inp))
            inp = input(": ")



if __name__ == "__main__":
    mainLoop()