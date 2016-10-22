\documentclass{report}
\usepackage[utf8]{inputenc}
\usepackage[a4paper,top=3cm,bottom=4cm]{geometry}
\usepackage[many]{tcolorbox}
\usepackage{verse}
\usepackage[official]{eurosym}
\usepackage[normalem]{ulem}
\usepackage{graphicx}
\usepackage[export]{adjustbox}

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
%%%%%%%%%%%%%

\usepackage[hyperfootnotes=false]{hyperref} % needs to be loaded last

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
                ${poem.datetime.strftime("%Y-%m-%d %H:%M:%S")}}
    \begin{tcolorbox}[colback=green!5,colframe=green!40!black,title=/u/${poem.submission_user},breakable]
        % if poem.submission_url is not None:
        \href{${poem.submission_url}}{[Link]}
            % if poem.imgfilename:
                \includegraphics[keepaspectratio,max width=0.5\textwidth, height=0.5\textwidth]{"${poem.imgfilename}"}
            % endif
        % else:
        ${poem.submission_content}
        % endif
    \end{tcolorbox}

    % for c in poem.parents:
        \begin{tcolorbox}[colback=blue!5,colframe=blue!40!black,title=/u/${c["author"]},breakable]
            ${c["body"]}
        \end{tcolorbox}
    % endfor

    \begin{tcolorbox}[colframe=black!40!black,${"breakable," if len([1 for c in poem.content if c == "\n"])>35 else ""}title=/u/${user_name} \href{${poem.link}}{[Link]}]
            \begin{verse}
                ${poem.content}
            \end{verse}
    \end{tcolorbox}
% endfor
\chapter{Statistics}
\large
${len(poems)} Poems
\begin{itemize}
\renewcommand{\labelitemi}{\dots}
\item containing an average of ${"%.1d".format(sum(len(poem.content.split(" ")) for poem in poems)/len(poems))} words.
\item totalling ${sum(len(poem.content.split(" ")) for poem in poems)} words.
\item which earned a total of ${sum(poem.gold or 0 for poem in poems)} months of reddit gold.
\end{itemize}
\end{document}