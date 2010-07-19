import sys
import urllib2
from BeautifulSoup import BeautifulSoup
import zipfile
import tempfile
import shutil

class onemanga_parser:
	"""This class has all the onemanga.com specific code. Privides nice methods to get manga list and
	download any chapter"""

	base_url = "http://www.onemanga.com"
	# Creo el dict vacio por si no corren primero get_manga_dict.
	manga_dict = {}
	chap_names = []
	chap_dict = {}

	def _init_ (self):
		pass

	def _extract_ch_subject_div(self, soup):
		# Me quedo con todos los campos que tiene el div tipo 'ch-subject'.
		full_list = soup.findAll("td", "ch-subject")
		# Extraigo la URL de los href que me quendan. Completo las URL. Extraigo el nombre.
		urls = [m.contents[0].attrs[0][1] for m in full_list]
		urls = [self.base_url+u for u in urls]
		names = [m.contents[0].contents[0] for m in full_list]
		# Armo un diccionario con nombre + urls.
		d = dict(zip(names, urls))
		return names,d

	def _download_urls (self, pag_names, file_names, pag_dict):
		for (num, name) in enumerate(pag_names):
			out = open(file_names[num],"w")
			img = urllib2.urlopen(pag_dict[name])
			out.write(img.read())
			out.close()

	def _create_cbz_file(self, file_name, file_list):
		# save the files in the files list into a PKZIP format .zip file
    		zout = zipfile.ZipFile(file_name, "w")
    		for fname in file_list:
    			zout.write(fname)
		zout.close()

	def get_manga_dict (self):
		"""Downloads the full manga list and returns a dictionary with the names as the keys and the urls
		as the values"""
		# Bajo la pagina con la lista de mangas.
		page = urllib2.urlopen(self.base_url + "/directory/")
		# Muuucha magia :)
		soup = BeautifulSoup(page, convertEntities=BeautifulSoup.HTML_ENTITIES)
		
		manga_names, self.manga_dict = self._extract_ch_subject_div(soup)
		return self.manga_dict

	def get_chapter_dict (self, manga_name):
		"""Returns a dict with chapter name as key and url as value. Returns and empty if manga is not in the
		manga list."""

		if not manga_name in self.manga_dict:
			raise NameError("Manga not in OneManga.com")

		# Bajo la pagina con la lista de caps de un manga y me guardo la URL de cada captitulo en un dict.
		page = urllib2.urlopen(self.manga_dict[manga_name])
		soup = BeautifulSoup(page)

		self.chap_names, self.chap_dict = self._extract_ch_subject_div(soup)
		# Tengo de dar vuelta el orden porque esta el mas nuevo al principio.
		self.chap_names.reverse()
		return self.chap_names, self.chap_dict

	def get_chapter_img_dict (self, chapter_name):
		if not chapter_name in self.chap_dict:
			raise NameError("Selected manga does not have this chapter")

		# La pagina tiene una sola lista, y quiero el primer item, el link al cap que buscan.
		page = urllib2.urlopen(self.chap_dict[chapter_name])
		soup = BeautifulSoup(page, convertEntities=BeautifulSoup.HTML_ENTITIES)
		s = soup.ul.li.contents[0].attrs[0][1]
		# Bajo la primer pagina del capitulo.
		page = urllib2.urlopen(self.base_url + s)
		soup = BeautifulSoup(page, convertEntities=BeautifulSoup.HTML_ENTITIES)
		# Extraigo la lista de paginas de este capitulo
		pages_list = soup.findAll("div","chapter-navigation")[0].contents[3].findAll("option")
		# Me quedo con la "base url" de las fotos del capitulo.
		base_url_img = '/'.join(soup.find ("img", "manga-page").attrs[1][1].split('/')[:-1])

		pag_url = [l.attrs[0][1] for l in pages_list]
		pag_url = [base_url_img+'/'+u+".jpg" for u in pag_url]
		pag_names = [l.contents[0] for l in pages_list]

		d = dict(zip(pag_names, pag_url))
		return pag_names,d

	def download_manga_chapter (self, manga, chapter_name):
		if self.chap_names == []:
			self.chap_names, self.chap_dict = self.get_chapter_dict(manga)

		pag_names, pag_dict = self.get_chapter_img_dict (chapter_name)
		# Creo la lista con los nombres de los archivos que quiero crear.
		tmp_dir = tempfile.mkdtemp()
		f_names = [tmp_dir + "/" + str(num).zfill(2) + "-" + chapter_name +"-"+name + ".jpg" for (num, name) in enumerate(pag_names)]
		# Bajo todas las imagenes!
		self._download_urls (pag_names, f_names, pag_dict)
		# Creo un .cbz con las imagenes
		cbz_name = str(self.chap_names.index(chapter_name)).zfill(4)+"-"+ chapter_name + ".cbz"
		self._create_cbz_file (cbz_name, f_names)
		# Borro el archivo temporal
		shutil.rmtree(tmp_dir)
		return cbz_name

