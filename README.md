# Sprog Backend

Backend for [https://almoturg.com/sprog/](https://almoturg.com/sprog/) and the [Sprog Android App](https://github.com/PaulKlinger/Sprog-App).

Gets new reddit comments by /u/Poem_for_your_sprog, creates pdf collections of them, and stores them as json. Results are uploaded to https://almoturg.com/sprog

In addition to the Python packages specified in requirements.txt the following external tools are required
* A LaTeX installation with XeLateX (e.g. [TexLive](https://www.tug.org/texlive/)) and the following packages: babel, geometry, tcolorbox, verse, eurosym, ulem, graphicx, subcaption, float, adjustbox, scalerel, fontspec, varwidth, longtable, booktabs, fancyvrb, microtype, titlesec, hyperref, xcolor
* [mogrify](http://www.imagemagick.org/script/mogrify.php) (part of [ImageMagick](http://www.imagemagick.org/))