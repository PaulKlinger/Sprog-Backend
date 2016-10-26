\documentclass{report}
\usepackage[english]{babel}
\usepackage[a4paper,top=3cm,bottom=4cm]{geometry}
\usepackage[many]{tcolorbox}
\usepackage{verse}
\usepackage[official]{eurosym}
\usepackage[normalem]{ulem}
\usepackage{graphicx}
\usepackage[export]{adjustbox}
\usepackage{scalerel}

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

\usepackage[hyperfootnotes=false]{hyperref} % needs to be loaded last
\usepackage{xcolor}
\hypersetup{
    colorlinks,
    linkcolor={red!50!black},
    citecolor={blue!50!black},
    urlcolor={blue!80!black}
}
\definecolor{babyblue}{rgb}{0.54, 0.81, 0.94}

\newcommand{\attrib}[1]{%
\nopagebreak{\raggedleft\footnotesize #1\par}}


\begin{document}
\begin{titlepage}\centering
\par\vspace*{7cm}
{\LARGE The Collected Reddit Poetry of\par}
{\LARGE /u/Poem\_for\_your\_sprog \par}
\vspace{5mm}
{\large \today \par}
\vfill

{\footnotesize For bug reports or suggestions contact /u/Almoturg.\par}
{\footnotesize The newest version of this file is available \href{https://drive.google.com/uc?export=download&confirm=PUC1&id=0B5rhAEnx4Q9wbWdkbXd1VnpzUEU}{here}.\par}
\end{titlepage}
% for i, poem in enumerate(poems):
    % if i==0 or (i+1<len(poems) and poem.datetime.year != poems[i-1].datetime.year):
    \chapter{${poem.datetime.year}}
    %endif
    \section*{\#${len(poems)-i} -- ${poem.submission_title}\\\
                ${poem.datetime.strftime("%Y-%m-%d %H:%M:%S")}}\label{${id_from_link(poem.link)}}
    \begin{tcolorbox}[enhanced, colback=green!5,colframe=green!40!black,title=/u/${poem.submission_user},breakable]
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
        \begin{tcolorbox}[enhanced, colback=blue!5,colframe=blue!40!black,title=/u/${c["author"]},breakable]
            ${c["body"]}
        \end{tcolorbox}
    % endfor

    \begin{tcolorbox}[enhanced, colframe=black!40!black,${"breakable," if poem.content.count("\\\\")+poem.content.count("\r\n\r\n")>40 or len(poem.content)>3000 else ""}
                      title={/u/${user_name} \href{${poem.link}}{\color{babyblue}{[Link]}} %
                      ${r"\scalerel*{\includegraphics{../gold.png}}{B}$\,\times\,"+str(poem.gold)+"$" if poem.gold else ""}}]
            \begin{verse}
                ${poem.content}
            \end{verse}
    \end{tcolorbox}
% endfor
\chapter{Statistics}
\large
\section*{${len(poems)} Poems}
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

\section*{Most gilded:}
\begin{enumerate}
% for p in sorted(poems, key=lambda x: x.gold or 0, reverse=True)[:15]:
\item \scalerel*{\includegraphics{../gold.png}}{B}\makebox[1cm]{$\,\times\,${p.gold}$\hfill} \hyperref[${id_from_link(p.link)}]{${make_snippet(p.content)}\ldots}
% endfor
\end{enumerate}

\section*{Most karma:}
\begin{enumerate}
% for p in sorted(poems, key=lambda x: x.score or 0, reverse=True)[:15]:
\item \textbf{${p.score}} \hyperref[${id_from_link(p.link)}]{${make_snippet(p.content)}\ldots}
% endfor
\end{enumerate}
\section*{Graphs}
\makebox[\textwidth][c]{
\includegraphics[width=1.3\textwidth]{monthsplot.pdf}
}
\end{document}