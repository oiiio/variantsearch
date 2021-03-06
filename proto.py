#!/usr/bin/python


import sys, getopt
import os
import re
import mongo
from Bio import Entrez


#assign eutils email
Entrez.email = "<email>"


#return list of protein alternate names
def altNames(protein):

    d = {'CYS': 'C', 'ASP': 'D', 'SER': 'S', 'GLN': 'Q', 'LYS': 'K',
    'ILE': 'I', 'PRO': 'P', 'THR': 'T', 'PHE': 'F', 'ASN': 'N',
    'GLY': 'G', 'HIS': 'H', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W',
    'ALA': 'A', 'VAL':'V', 'GLU': 'E', 'TYR': 'Y', 'MET': 'M'} #IUPAC table

    dr = {'C':'Cys' , 'D':'Asp' , 'S':'Ser' , 'Q':'Gln' , 'K':'Lys' ,
    'I':'Ile' , 'P':'Pro' , 'T':'Thr' , 'F':'Phe' , 'N':'Asn' , 'G':'Gly' ,
    'H':'His' , 'L':'Leu' , 'R':'Arg' , 'W':'Trp' , 'A':'Ala', 'V':'Val' , 'E':'Glu' ,
    'Y':'Tyr' , 'M':'Met'} #reverse table


    threePattern = re.compile("[A-Z][a-z][a-z]")
    #onePattern = re.compile("(^[A-Z][0-9])([0-9][A-Z]$|_[A-Z][0-9]")
    oneChar = ""
    threeChar = ""
    #starChar = ""
    #create protein query with 3-letter code as input
    if re.search(threePattern,protein):
        oneChar = protein
        for triple in re.findall(threePattern, protein):
            #if (triple == "Ter"):
            #    oneChar = re.sub("Ter","X",oneChar)
                #starChar = re.sub("Ter","*",starChar)
                #starCount = int(1)
            if (triple == "ins" or triple == "del"):
                next;
            elif (triple != "Ter"):
                upperTriple = triple.upper()
                if (upperTriple in d): #does nothing if no recognized letter in IUPAC table
                    oneChar =re.sub(triple, d[upperTriple] ,oneChar)
        threeChar = protein

    #create protein queries with the 1-letter codes as input
    if re.search(threePattern,protein) is None:
        threeChar = protein
        for one in re.findall("[A-Z]",protein):
            if ( one != "X" ):
                if (one in dr):
                    threeChar = re.sub(one,dr[one],protein) # does nothing if the letter doesn't exist in the IUPAC table

        oneChar = protein

    #if there is a stop mutation noted
    starPattern = re.compile("[*X]|Ter")
    oneStar = oneChar
    oneX = oneChar
    oneTer = oneChar
    threeStar = threeChar
    threeX = threeChar
    threeTer = threeChar
    starCount = int(0) # don't output starChar unless the deletion notation requries output of both X and * queries
    if re.search(starPattern,oneChar):
        starCount = int(1)
        #changes all terminal notations into an X, Ter, or *. Does not do combinations of symbols if there is more than one instance present
        for star in re.findall(starPattern,oneChar):
            oneStar = re.sub(star,'*',oneStar)
            oneX = re.sub(star,'X',oneX)
            oneTer = re.sub(star,'Ter',oneTer)

    if re.search(starPattern,threeChar):
        starCount = int(1)
        for star in re.findall(starPattern,threeChar):
            threeStar = re.sub(star,'*',threeStar)
            threeX = re.sub(star,'X',threeX)
            threeTer = re.sub(star,'Ter',threeTer)


    if starCount == 1:
        return [oneChar,oneX,oneStar,oneTer,threeChar,threeX,threeStar,threeTer]
    elif starCount==0:
        return [oneChar,threeChar]



def clinVar(rsid,gene,oneChar):

    print "ClinVar_____",rsid,"_____",oneChar,"_____",gene


    if rsid is not None:
        handle = Entrez.esearch(db="clinvar",term=rsid+" AND "+gene+"[Gene]",retmax=20)
        record = Entrez.read(handle)
        rsidList = record["IdList"]
    elif rsid is None:
        rsidList = []

    if oneChar[0] is not None:
        protList = []
        if len(oneChar) == 1:
            handle = Entrez.esearch(db="clinvar", term=oneChar[0]+" AND "+gene+"[Gene]",retmax=20)
            record = Entrez.read(handle)
            protList = record["IdList"]
        elif len(oneChar) ==2:
            for symbol in oneChar:
                handle = Entrez.esearch(db="clinvar", term=symbol+" AND "+gene+"[Gene]",retmax=20)
                record = Entrez.read(handle)
                protList.extend(record["IdList"])
    elif oneChar[0] is None:
        protList = []


    if len(rsidList) > 0 and len(protList) > 0:
        uniqueClin = set(rsidList + protList)
    if len(rsidList) > 0 and len(protList) == 0:
        uniqueClin = rsidList
    if len(rsidList) == 0 and len(protList) > 0:
        uniqueClin = protList


    uniqueStr = ','.join(uniqueClin)
    print "ClinVar_____",uniqueStr
#    record = Entrez.read(Entrez.elink(dbfrom="clinvar",db="pubmed",id=pmid))

    if len(uniqueClin) > 0:
        handle = Entrez.elink(dbfrom="clinvar",db="pubmed",id=uniqueStr,retmax=20)
        record = Entrez.read(handle)
        clinOut = []
        setUp = record[0]["LinkSetDb"][0]["Link"]
        for link in setUp:
            clinOut.append(link["Id"])
            return clinOut
    elif len(uniqueClin) == 0:
        clinOut = []
        return clinOut

def search(gene,rsid,protQueries):
    print gene," ",rsid," ",protQueries
    if (rsid is not None):
        handle = Entrez.esearch(db="pubmed", term=rsid+" AND "+gene+"[Gene]", retmax=20)
        record = Entrez.read(handle)
        rsidList = record["IdList"]
    elif rsid is None:
        rsidList = []
    print rsidList
    #protein search
    if (protQueries[0] is not None):
        protList = []
        for prot in protQueries:
            handle = Entrez.esearch(db="pubmed", term=prot+" AND "+gene+"[Gene]", retmax=20)
            record = Entrez.read(handle)
            protList.extend(record["IdList"])
    elif (protQueries[0] is None):
        protList = []

    print protList


    if len(protQueries) > 2:
        clinput = [protQueries[1],protQueries[2]]
        clinList = clinVar(rsid,gene,clinput)
    elif len(protQueries) == 2:
        clinput = [protQueries[0]]
        clinList = clinVar(rsid,gene,clinput)

    uniques = set(rsidList + protList + clinList)

    #get abstracts and such
    uniquesGrab = ','.join(uniques)
    print uniquesGrab
    handle = Entrez.efetch(db="pubmed", id=uniquesGrab, retmode='xml',rettype='abstract')
    record = Entrez.read(handle)
    searchOut = {}
    for article in record:
        title = article['MedlineCitation']['Article']['ArticleTitle']
        pmidEl = article['MedlineCitation']['PMID']
        print pmidEl
        try:
            abstract = article['MedlineCitation']['Article']['Abstract']['AbstractText'][0]
        except:
            abstract = "Abstract not available."
        searchOut[pmidEl]=[title,abstract]

    return searchOut




def main(argv):
    rsid = ''
    protein = ''
    gene = ''
    try:
        opts, args = getopt.getopt(argv,"hr:p:g:",["rsid=","protein=","gene="])
    except getopt.GetoptError:
        print 'proto.py -r <rsid> -p <protein position (e.g Arg59His)> -g <gene>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'proto.py -r <rsid> -p <protein position (e.g Arg59His, W49*, Ser728Ilefs)> -g <gene>'
            sys.exit()
        elif opt in ("-r", "--rsid"):
            rsid = arg
        elif opt in ("-p", "--protein"):
            protein = arg
        elif opt in ("-g", "--gene"):
            gene = arg

    if len(rsid) < 1 and len(protein) < 1 :
        print 'Requires rsid and/or protein field'
        sys.exit(2)
    if len(gene) <1 :
        print 'Gene is required'
        sys.exit(2)
    if len(rsid) < 1:
        rsid = None
    if len(protein) < 1:
        protein = None

    if protein is not None:
        protein = re.sub("p\.","",protein)
        protQueries = altNames(protein)
    elif protein is None:
        protQueries = [None,None]

    if len(protQueries) > 2:
        protDb = protQueries[1]
        #dbTest = mongo.inDb(protQueries[1],gene,rsid)
    elif len(protQueries) == 2:
        protDb = protQueries[0]
        #dbTest = mongo.inDb(protQueries[0],gene,rsid)

    searchDict = search(gene,rsid,protQueries)
    insert = mongo.variantInput(protDb,gene,rsid,searchDict)
    #Not ready yet, need to develop rules for handling multiple document hits due to typos in queries or inconsistent protein/rsid pairs in queries
    #elif dbTest is True:
    #    searchDict = mongo.paperPull(protDb,gene,rsid)
    print searchDict


if __name__ == "__main__":
    main(sys.argv[1:])
