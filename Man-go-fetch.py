#!/usr/bin/env python
import sys
from optparse import OptionParser
from onemanga_parser import *

class Man_go_fetch: 
	"""Clase que contiene la funcionalidad del programa principal"""
	def __init__(self, verbose):
		self.verbose = verbose
		self.om = onemanga_parser()
		if verbose:
			print ("Getting manga list from onemanga.com...")
		self.manga_dict = self.om.get_manga_dict()

	def _create_chapter_slice(self, manga, from_c, to_c):
		if self.verbose:
			print "Fetching chapter list..."
		cn, cd = self.om.get_chapter_dict(manga)
		to_c = ' '.join([manga, to_c])
		from_c = ' '.join([manga, from_c])
		return cn[cn.index(from_c):(cn.index(to_c)+1)]

	def _download_chapters(self, manga, chapters):
		total = len(chapters)
		for (i,c) in enumerate(chapters):
			if self.verbose == True:
				print "(%i out of %d) Fetching... " % (i+1, total),
				sys.stdout.flush()
			chap = self.om.download_manga_chapter(manga, c)
			if self.verbose == True:
				print "%s \t OK!" % (chap)
				sys.stdout.flush()

	def print_manga_list(self):
		print '\n'.join(self.manga_dict.keys())
		print "\nTotal: %d mangas." % (len(self.manga_dict))

	def get_manga_chapters(self, manga):
		if self.verbose:
			print "Fetching chapter list..."
		cn, cd = self.om.get_chapter_dict(manga)
		print '\n'.join(cn)
		print "\nTotal: %d chapters." % (len(cn))

	def download_manga_chapters(self, manga, from_c, to_c):
		chapters = self._create_chapter_slice(manga, from_c, to_c)
		self._download_chapters(manga, chapters)

	def download_full_manga(self, manga):
		if self.verbose:
			print "Fetching chapter list..."
		cn, cd = self.om.get_chapter_dict(manga)
		self._download_chapters(manga, cn)
		
# Declaro el parser de argumentos con sus opciones.
parser = OptionParser(version="%prog 0.1" )

parser.add_option("-l","--list-manga",dest="list_manga", default=False,
	action="store_true", help="list all available mangas and exit.")
parser.add_option("-c","--list-chapters",dest="list_chapters", default=False,
	action="store_true", help="list all chapters from selected manga and exit.")
parser.add_option("-m","--manga",dest="manga",
	help="name of the manga to download.", metavar="MANGA")
parser.add_option("-f","--from-chapter",dest="from_chapter",
	help="first chapter to download, inclusive.", metavar="NUM")
parser.add_option("-t","--to-chapter",dest="to_chapter",
	help="last chapter to download, inclusive.", metavar="NUM")
parser.add_option("-a","--all",dest="all", default=False,
	action="store_true", help="download entire manga.",)
parser.add_option("-v","--verbose",dest="verbose", default=False,
	action="store_true", help="increase output level.",)

(options, args) = parser.parse_args()

# Me fijo que tenga algo para hacer...
if options.manga == None and not options.list_manga:
	print ("You need to specify a manga name")
	sys.exit(1)

p = Man_go_fetch(options.verbose)

if options.list_manga:
	p.print_manga_list()
	sys.exit(0)

if options.manga != None and options.list_chapters:
	c = p.get_manga_chapters(options.manga)
	sys.exit(0)

if options.all == False and (options.from_chapter == None or options.to_chapter == None):
	print ("You have to tell me which chapters to download!")
	sys.exit(1)
#	p.get_manga(options.manga, from_chapter, to_chapter, verbose)
elif (options.from_chapter != None and options.to_chapter != None):
	p.download_manga_chapters(options.manga, options.from_chapter, options.to_chapter)

elif (options.all == True):
	p.download_full_manga(options.manga)

sys.exit(0)
