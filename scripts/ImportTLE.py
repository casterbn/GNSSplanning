"""
-------------------------------------------------------------------------------
Name:        ImportTLE
Purpose:     This script was used to create the initial satellite data
             repository by converting Celestrak TLE files into a
             satellited.dat and .cat files.
             You should have a .cat file for each category as well as a
             satellites.dat file in the ./sat/ folder
Created:     2017 by Cesc Masdeu Ferrer
Licence:     Free
------------------------------------------------------------------------------
"""
import os
import string
import urllib

def Import_TLE():

    # Satellite groups
    groups = {
        "gps-ops" : "GPS",
        "glo-ops" : "Glonass",
        "galileo" : "Galileo",
        "beidou" : "BeiDou"
    }

    # URL TLE files
    urlprefix = "http://celestrak.com/NORAD/elements/"
    plugin_dir = os.path.dirname(__file__)

    for group, name in groups.iteritems():
        webfile = urlprefix + group + ".txt"
        localfile =  plugin_dir + '/tle/' + group + ".txt"

        urllib.urlretrieve (webfile, localfile)


    # For each input file
    for group, name in groups.iteritems():

        # open TLE file for reading
        tlefile = open(plugin_dir +'/tle/' + group + '.txt', 'r')

        # create category file
        category = plugin_dir + "/cat/" + group + ".cat"
        catfile = open(category, 'w')

        # first line is the group name
        catfile.write(name+'\n')

        while 1:
            # read three lines at a time; strip trailing whitespaces
            line0 = tlefile.readline().strip()

            if not line0:
                break
            line1 = tlefile.readline().strip()
            line2 = tlefile.readline().strip()

            # catalog number; strip leading zeroes
            catnum = line1[2:7].lstrip('0')

            # add satellite to category
            catfile.write(catnum+'\n')

            # read satellite Names and IDs from satellitesIDs.sat
            satIDs = open(plugin_dir + '/sat/' + 'satellitesID.csv', 'r')
            for line in satIDs:

                if line[0:5] != catnum:
                    line3 = catnum + " NULL NULL NULL NULL NULL NULL"
                else:
                    line3 = line
                    break
            satIDs.close()

            # add TLE and satellites names and IDs to satellite file
            satfile = open(plugin_dir + '/sat/' + catnum + '.sat','w')

            satfile.write(line0+'\n')
            satfile.write(line1+'\n')
            satfile.write(line2+'\n')
            satfile.write(line3+'\n')

            satfile.close()

        # close TLE and CAT files
        tlefile.close()
        catfile.close()

