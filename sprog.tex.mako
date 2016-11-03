\documentclass{report}
\usepackage[english]{babel}
% if small:
\usepackage[paperheight=180mm,paperwidth=120mm,top=.5cm,bottom=.5cm,left=.5cm,right=.5cm]{geometry}
% else:
\usepackage[a4paper,top=3cm,bottom=4cm]{geometry}
% endif

\usepackage[many]{tcolorbox}
\usepackage{verse}
\usepackage[official]{eurosym}
\usepackage[normalem]{ulem}
\usepackage{graphicx}
\usepackage[export]{adjustbox}
\usepackage{scalerel}
\usepackage{fontspec}
\usepackage{varwidth} % variable width minipage for centering poems

\usepackage{longtable,booktabs}
\usepackage{fancyvrb}
\usepackage{microtype}
\setlength{\emergencystretch}{3em}  % prevent overfull lines
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

%%%%%%%%%%%%%%%%
%% Don't print "Chapter N" at start of chapter
\usepackage[pagestyles]{titlesec}
\titleformat{\chapter}[display]{\normalfont\bfseries}{}{0pt}{\Huge}
\newpagestyle{mystyle}
{\sethead[][][\chaptertitle]{}{}{}\setfoot{}{\thepage}{}}
\pagestyle{mystyle}
%% reduce margin before chapter
\titlespacing*{\chapter}{0pt}{10pt}{25pt}
%%%%%%%%%%%%%

\PassOptionsToPackage{hyphens}{url}\usepackage[hyperfootnotes=false]{hyperref} % needs to be loaded last
\usepackage{xcolor}
\hypersetup{
    colorlinks,
    linkcolor={red!50!black},
    citecolor={blue!50!black},
    urlcolor={blue!80!black}
}
\definecolor{babyblue}{rgb}{0.54, 0.81, 0.94}
\definecolor{posttitle}{RGB}{49, 107, 38}
\definecolor{commenttitle}{RGB}{48, 80, 124}
\definecolor{poemtitle}{RGB}{25, 25, 25}

\newcommand{\attrib}[1]{%
\nopagebreak{\raggedleft\footnotesize #1\par}}

\definecolor{textgray}{RGB}{40,40,40}
\newcommand\titlefont[1]{{\setmainfont{PatuaOne-Regular.otf}[Path=../fonts/]\color{textgray}{#1}}}

\setmainfont{DroidSerif_modified.ttf}[Path=../fonts/,
BoldFont = DroidSerif-Bold_modified.ttf ,
ItalicFont = DroidSerif-Italic_modified.ttf,
BoldItalicFont = DroidSerif-BoldItalic_modified.ttf]

\definecolor{quotebar}{RGB}{150, 150, 150}
\newtcolorbox{blockquote}{blanker, breakable,
      left=3mm, right=3mm, top=1mm, bottom=1mm,
      borderline west={1pt}{0pt}{quotebar},
      before upper=\indent, parbox=false}

% if small:
\setlength{\leftmargini}{1em}
% endif

\begin{document}
\begin{titlepage}\centering
\par\vspace*{${"5cm" if small else "7cm"}}
\titlefont{
{\huge The Collected Reddit Poetry of\par}
{\huge /u/Poem\_for\_your\_sprog \par}
\vspace{5mm}
{\Large \today \par}}
\vfill

{\small For bug reports or suggestions contact /u/Almoturg.\par}
{\small The newest version of this file is available \href{https://almoturg.com/sprog}{here}.\par}
\end{titlepage}
% for i, poem in enumerate(poems):
    % if i==0 or (i+1<len(poems) and poem.datetime.year != poems[i-1].datetime.year):
    \chapter[${poem.datetime.year}]{\titlefont{${poem.datetime.year}}}
    %endif
    \section*{\titlefont{\#${len(poems)-i} -- ${poem.submission_title}\\\
                ${poem.datetime.strftime("%Y-%m-%d %H:%M:%S")}}}\label{${id_from_link(poem.link)}}
    \begin{tcolorbox}[enhanced, colback=posttitle!5,colframe=posttitle,title=/u/${poem.submission_user},breakable]
        % if poem.submission_url is not None:
        \href{${poem.submission_url}}{[Link]}
            % if poem.imgfilename:

                \includegraphics[keepaspectratio,max width=0.5\textwidth, max height=0.5\textwidth]{"${poem.imgfilename}"}
            % endif
        % else:
        ${poem.submission_content}
        % endif
    \end{tcolorbox}

    % for c in poem.parents:
        \begin{tcolorbox}[enhanced, colback=commenttitle!5,colframe=commenttitle,title=/u/${c["author"]},breakable]
            ${c["body"]}
        \end{tcolorbox}
    % endfor
    <%
    if ((small and (poem.content.count("\\\\")+poem.content.count("\r\n\r\n")+poem.content.count("\n\n")+poem.content.count("fleuron")*3>24 or len(poem.content)>1200))
    or (not small and (poem.content.count("\\\\")+poem.content.count("\r\n\r\n")+poem.content.count("\n\n")+poem.content.count("fleuron")*3>40 or len(poem.content)>3000))):
        breakable = "breakable,"
    else:
        breakable = ""
    %>
    \begin{tcolorbox}[enhanced, colback=poemtitle!5, colframe=poemtitle, ${breakable}
                      title={/u/${user_name} \href{${poem.link}}{\color{babyblue}{[Link]}} %
                      ${r"\scalerel*{\includegraphics{../gold.png}}{B}$\,\times\,"+str(poem.gold)+"$" if poem.gold else ""}}]
            ${"" if small else "\\vspace{1.5em}"}
            ${"\\begin{center}\\begin{varwidth}[t]{\\textwidth}" if not breakable else ""}
                ${poem.content}
            ${"\\end{varwidth}\\end{center}" if not breakable else ""}
            ${"" if small else "\\vspace{.2em}"}
    \end{tcolorbox}
% endfor
\chapter[Statistics]{\titlefont{Statistics}}
\large
\section*{\titlefont{${len(poems)} Poems}}
\begin{itemize}
\renewcommand{\labelitemi}{\dots}
\item containing an average of ${"{:.2f}".format(sum(len(poem.content.split(" ")) for poem in poems)/len(poems))} words.
\item totalling ${"{:,}".format(sum(len(poem.content.split(" ")) for poem in poems))} words.
<% median, min, min_link = posting_time_stats(poems) %>
\item posted a median of ${median} after the parent comment.
\item the fastest of which was posted \hyperref[${min_link}]{${min}} after the parent comment.
\item at an average depth of ${"{:.2f}".format(statistics.mean([float(len(p.parents)) for p in poems]))}.
\item which received a total of ${"{:,}".format(sum(poem.gold or 0 for poem in poems))} months of Reddit gold.
\item with a median score of ${"{:,.0f}".format(statistics.median(p.score for p in poems if p.score is not None))} karma.
\item with a combined score of ${"{:,}".format(sum(p.score or 0 for p in poems))} karma.
\end{itemize}

\section*{\titlefont{Most gilded:}}
\begin{enumerate}
% for p in sorted(poems, key=lambda x: x.gold or 0, reverse=True)[:15]:
\item \scalerel*{\includegraphics{../gold.png}}{B}\makebox[1cm]{$\,\times\,${p.gold}$\hfill} \hyperref[${id_from_link(p.link)}]{${make_snippet(p.content)}\ldots}
% endfor
\end{enumerate}

\section*{\titlefont{Most karma:}}
\begin{enumerate}
% for p in sorted(poems, key=lambda x: x.score or 0, reverse=True)[:15]:
\item \textbf{${p.score}} \hyperref[${id_from_link(p.link)}]{${make_snippet(p.content)}\ldots}
% endfor
\end{enumerate}
\section*{\titlefont{Graphs}}
\makebox[\textwidth][c]{
\includegraphics[width=${"1.3" if not small else ""}\textwidth]{monthsplot.pdf}
}
\end{document}