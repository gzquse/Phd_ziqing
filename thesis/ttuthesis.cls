%% ttuthesis.cls — Texas Tech University thesis/dissertation class
%% Written against the TTU Graduate School Formatting Manual (Revised Feb 2026)
%% and the ETD Checklist (SP2024). Not an official Graduate School template:
%% "the Graduate School does not supply an approved LaTeX template."
%%
%% Options:
%%   dissertation | thesis        (default: dissertation)
%%   doublespacing | onehalfspacing (default: doublespacing)
%%   leftmargin15 | leftmargin10  (default: leftmargin15 = 1.5in left margin)
%%   draft                        (adds line numbers / DRAFT watermark off by default)
%%
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ttuthesis}[2026/09/16 v1.0 Texas Tech University thesis class]

\RequirePackage{etoolbox}
\RequirePackage{ifthen}

\newif\if@ttudissertation \@ttudissertationtrue
\newif\if@ttudouble \@ttudoubletrue
\newif\if@ttuwideleft \@ttuwidelefttrue
\newif\if@ttudraft \@ttudraftfalse

\DeclareOption{dissertation}{\@ttudissertationtrue}
\DeclareOption{thesis}{\@ttudissertationfalse}
\DeclareOption{doublespacing}{\@ttudoubletrue}
\DeclareOption{onehalfspacing}{\@ttudoublefalse}
\DeclareOption{leftmargin15}{\@ttuwidelefttrue}
\DeclareOption{leftmargin10}{\@ttuwideleftfalse}
\DeclareOption{draft}{\@ttudrafttrue}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{report}}
\ProcessOptions\relax

\LoadClass[12pt,oneside,letterpaper,openany]{report}

% ---------- Fonts: 12 pt serif (Times-like), black ----------
\RequirePackage[T1]{fontenc}
\RequirePackage[utf8]{inputenc}
\RequirePackage{mathptmx}
\RequirePackage[scaled=0.92]{helvet}
\RequirePackage{courier}
\RequirePackage{microtype}

% ---------- Geometry: 1.5in (or 1in) left; 1in top/right/bottom ----------
% Running header baseline 0.5in from top edge; page number 0.5in from bottom edge.
\RequirePackage{geometry}
\if@ttuwideleft
  \geometry{letterpaper,left=1.5in,right=1in,top=1in,bottom=1in,
            headheight=14pt,headsep=22pt,footskip=0.5in,
            includehead=false,includefoot=false,nomarginpar}
\else
  \geometry{letterpaper,left=1in,right=1in,top=1in,bottom=1in,
            headheight=14pt,headsep=22pt,footskip=0.5in,
            includehead=false,includefoot=false,nomarginpar}
\fi

% ---------- Spacing ----------
\RequirePackage{setspace}
\if@ttudouble
  \newcommand{\ttubodyspacing}{\doublespacing}
  \newcommand{\ttubodystretch}{2.0}
\else
  \newcommand{\ttubodyspacing}{\onehalfspacing}
  \newcommand{\ttubodystretch}{1.5}
\fi
\AtBeginDocument{\ttubodyspacing}

% Dangling-heading / widow / club protection
\clubpenalty=10000
\widowpenalty=10000
\displaywidowpenalty=10000
\RequirePackage{needspace}

% ---------- Metadata macros ----------
\newcommand{\ttu@title}{Title}
\newcommand{\ttu@author}{Author Name}
\newcommand{\ttu@credentials}{B.S.}
\newcommand{\ttu@department}{Computer Science}
\newcommand{\ttu@degree}{Doctor of Philosophy}
\newcommand{\ttu@month}{May}
\newcommand{\ttu@year}{2026}
\newcommand{\ttu@chair}{Chair Name, Ph.D.}
\newcommand{\ttu@dean}{Mark Sheridan, Ph.D.}
\newcommand{\ttu@committee}{}

\renewcommand{\title}[1]{\renewcommand{\ttu@title}{#1}}
\renewcommand{\author}[1]{\renewcommand{\ttu@author}{#1}}
\newcommand{\credentials}[1]{\renewcommand{\ttu@credentials}{#1}}
\newcommand{\department}[1]{\renewcommand{\ttu@department}{#1}}
\newcommand{\degree}[1]{\renewcommand{\ttu@degree}{#1}}
\newcommand{\graduationmonth}[1]{\renewcommand{\ttu@month}{#1}}
\newcommand{\graduationyear}[1]{\renewcommand{\ttu@year}{#1}}
\newcommand{\committeechair}[1]{\renewcommand{\ttu@chair}{#1}}
\newcommand{\graduatedean}[1]{\renewcommand{\ttu@dean}{#1}}
% \committeemember{Name, Ph.D.} — call once per non-chair member, in order.
\newcommand{\committeemember}[1]{\g@addto@macro\ttu@committee{\par\vspace{12pt}#1}}

% ---------- Headers and footers ----------
\RequirePackage{fancyhdr}
\newcommand{\ttu@runninghead}{Texas Tech University, \ttu@author, \ttu@month\ \ttu@year}
% Page number centered on the physical page (not on the text block): shift by half the margin difference.
\newlength{\ttu@footshift}
\if@ttuwideleft \setlength{\ttu@footshift}{-0.25in}\else \setlength{\ttu@footshift}{0pt}\fi
\fancypagestyle{ttumain}{%
  \fancyhf{}%
  \renewcommand{\headrulewidth}{0pt}%
  \renewcommand{\footrulewidth}{0pt}%
  \fancyhead[R]{\fontsize{11}{13}\selectfont\ttu@runninghead}%
  \fancyfoot[C]{\hspace*{\ttu@footshift}\thepage}%
}
\fancypagestyle{ttuempty}{\fancyhf{}\renewcommand{\headrulewidth}{0pt}\renewcommand{\footrulewidth}{0pt}}
\fancypagestyle{plain}{%
  \fancyhf{}%
  \renewcommand{\headrulewidth}{0pt}%
  \fancyhead[R]{\fontsize{11}{13}\selectfont\ttu@runninghead}%
  \fancyfoot[C]{\hspace*{\ttu@footshift}\thepage}%
}
\pagestyle{ttumain}

% ---------- Level-1 headings: centered, ALL CAPS, "CHAPTER I" on the line above ----------
\RequirePackage{titlesec}
\renewcommand{\thechapter}{\Roman{chapter}}
\newcommand{\ttu@levelonefont}{\normalfont\fontsize{14}{16}\selectfont\bfseries}
\titleformat{\chapter}[display]
  {\ttu@levelonefont\centering\singlespacing}
  {\MakeUppercase{\chaptertitlename}\ \thechapter}
  {6pt}
  {\MakeUppercase}
  [\vspace{6pt}]
\titlespacing*{\chapter}{0pt}{0pt}{24pt}

% TOC chapter entries in caps, matching the typeset chapter headings (ETD checklist item 25)
\newcommand{\ttutocuc}[1]{\texorpdfstring{\MakeUppercase{#1}}{#1}}
\patchcmd{\@chapter}{\addcontentsline{toc}{chapter}{\protect\numberline{\thechapter}#1}}
  {\addcontentsline{toc}{chapter}{\protect\numberline{\thechapter}\protect\ttutocuc{#1}}}{}{\ClassWarning{ttuthesis}{Could not patch \string\@chapter for uppercase TOC entries}}

% Unnumbered level-1 heading used by front matter, References, and the Appendix banner
\newcommand{\ttuleveloneheading}[1]{%
  \clearpage
  \begingroup\ttu@levelonefont\centering\singlespacing
  \MakeUppercase{#1}\par
  \endgroup
  \vspace{24pt}}

% Subheadings: distinct, consistent levels; decimal numbering (=> decimal floats/equations)
\renewcommand{\thesection}{\arabic{chapter}.\arabic{section}}
\renewcommand{\thesubsection}{\thesection.\arabic{subsection}}
\renewcommand{\thesubsubsection}{\thesubsection.\arabic{subsubsection}}
\titleformat{\section}{\needspace{3\baselineskip}\normalfont\fontsize{13}{15}\selectfont\bfseries\singlespacing}{\thesection}{0.6em}{}
\titleformat{\subsection}{\needspace{3\baselineskip}\normalfont\normalsize\bfseries\itshape\singlespacing}{\thesubsection}{0.6em}{}
\titleformat{\subsubsection}{\needspace{3\baselineskip}\normalfont\normalsize\itshape\singlespacing}{\thesubsubsection}{0.6em}{}
\titlespacing*{\section}{0pt}{18pt}{8pt}
\titlespacing*{\subsection}{0pt}{14pt}{6pt}
\titlespacing*{\subsubsection}{0pt}{12pt}{4pt}
\setcounter{secnumdepth}{3}

% Floats and equations numbered per chapter, using Arabic chapter number (Table 3.1, Figure 4.2, Eq. (2.5))
\RequirePackage{amsmath,amssymb,amsthm}
\numberwithin{equation}{chapter}
\numberwithin{figure}{chapter}
\numberwithin{table}{chapter}
% Arabic chapter numbers for floats/equations even though chapter headings use Roman numerals
\renewcommand{\thefigure}{\arabic{chapter}.\arabic{figure}}
\renewcommand{\thetable}{\arabic{chapter}.\arabic{table}}
\renewcommand{\theequation}{\arabic{chapter}.\arabic{equation}}

% ---------- Captions: tables above, figures below; "Table 2.1. Title"; single spaced ----------
\RequirePackage[font={singlespacing,normalsize},labelfont=bf,labelsep=period,justification=justified,singlelinecheck=false]{caption}
\captionsetup[table]{position=above,skip=6pt}
\captionsetup[figure]{position=below,skip=8pt}
\RequirePackage{subcaption}
\RequirePackage{booktabs,multirow,longtable,threeparttable,array,tabularx}
\RequirePackage{graphicx}
\RequirePackage{float}

% ---------- TOC / LOT / LOF ----------
\RequirePackage{tocloft}
\setcounter{tocdepth}{2}
\renewcommand{\cfttoctitlefont}{\hfill\ttu@levelonefont}
\renewcommand{\cftaftertoctitle}{\hfill\hfill}
\renewcommand{\cftlottitlefont}{\hfill\ttu@levelonefont}
\renewcommand{\cftafterlottitle}{\hfill\hfill}
\renewcommand{\cftloftitlefont}{\hfill\ttu@levelonefont}
\renewcommand{\cftafterloftitle}{\hfill\hfill}
\renewcommand{\contentsname}{TABLE OF CONTENTS}
\renewcommand{\listtablename}{LIST OF TABLES}
\renewcommand{\listfigurename}{LIST OF FIGURES}
\renewcommand{\cftchapfont}{\normalfont\raggedright}
\renewcommand{\cftchappagefont}{\normalfont}
\renewcommand{\cftchapleader}{\cftdotfill{\cftdotsep}}
\renewcommand{\cftchappresnum}{\MakeUppercase{\chaptername}\ }
\renewcommand{\cftchapaftersnum}{.}
\setlength{\cftchapnumwidth}{6.6em}
\setlength{\cftbeforechapskip}{0.6\baselineskip}
\setlength{\cftbeforesecskip}{0.35\baselineskip}
\setlength{\cftbeforesubsecskip}{0.2\baselineskip}
\setlength{\cftsecindent}{2em}
\setlength{\cftsubsecindent}{4em}
\setlength{\cftsecnumwidth}{2.6em}
\setlength{\cftsubsecnumwidth}{3.4em}
\setlength{\cftbeforetabskip}{0.6\baselineskip}
\setlength{\cftbeforefigskip}{0.6\baselineskip}
\setlength{\cfttabnumwidth}{3em}
\setlength{\cftfignumwidth}{3em}
\setlength{\cftbeforetoctitleskip}{0pt}
\setlength{\cftaftertoctitleskip}{24pt}
\setlength{\cftbeforelottitleskip}{0pt}
\setlength{\cftafterlottitleskip}{24pt}
\setlength{\cftbeforeloftitleskip}{0pt}
\setlength{\cftafterloftitleskip}{24pt}
% Single-space within multi-line entries: tocloft entries are set in the current spacing,
% so we switch to single spacing while typesetting the lists.
\newcommand{\ttutableofcontents}{\clearpage\begingroup\singlespacing\tableofcontents\endgroup}
\newcommand{\ttulistoftables}{\clearpage\begingroup\singlespacing\phantomsection\addcontentsline{toc}{chapter}{LIST OF TABLES}\listoftables\endgroup}
\newcommand{\ttulistoffigures}{\clearpage\begingroup\singlespacing\phantomsection\addcontentsline{toc}{chapter}{LIST OF FIGURES}\listoffigures\endgroup}

% ---------- Hyperlinks: present but printed black ----------
\RequirePackage[hidelinks,bookmarksnumbered,pdfusetitle]{hyperref}
\RequirePackage[nameinlink,capitalise,noabbrev]{cleveref}
\crefname{chapter}{Chapter}{Chapters}
\Crefname{chapter}{Chapter}{Chapters}
\AtBeginDocument{\hypersetup{pdftitle={\ttu@title},pdfauthor={\ttu@author},pdflang={en-US}}}

% ---------- Title page ----------
\newcommand{\ttu@doctype}{\if@ttudissertation A Dissertation\else A Thesis\fi}
\newcommand{\maketitlepage}{%
  \clearpage
  \thispagestyle{ttuempty}%
  \begingroup
  \singlespacing\centering
  \null\vspace*{0.1in}
  {\normalsize \ttu@title\par}
  \vspace{22pt}
  by\par
  \vspace{12pt}
  \ttu@author, \ttu@credentials\par
  \vspace{22pt}
  \ttu@doctype\par
  \vspace{12pt}
  In\par
  \vspace{12pt}
  \ttu@department\par
  \vspace{22pt}
  Submitted to the Graduate Faculty\\
  of Texas Tech University in\\
  Partial Fulfillment of\\
  the Requirements for\\
  the Degree of\par
  \vspace{14pt}
  \MakeUppercase{\ttu@degree}\par
  \vspace{22pt}
  Approved\par
  \vspace{12pt}
  \ttu@chair\\
  Chair of the Committee\par
  \ttu@committee\par
  \vspace{22pt}
  \ttu@dean\\
  Dean of the Graduate School\par
  \vspace{22pt}
  \ttu@month, \ttu@year\par
  \endgroup
  \clearpage}

% ---------- Copyright page: centered both ways, unnumbered ----------
\newcommand{\makecopyrightpage}{%
  \clearpage
  \thispagestyle{ttuempty}%
  \null\vfill
  \begin{center}Copyright \ttu@year, \ttu@author\end{center}
  \vfill\null
  \clearpage}

% ---------- Front matter environments ----------
\newenvironment{acknowledgments}{%
  \clearpage\pagenumbering{roman}\setcounter{page}{2}\pagestyle{ttumain}%
  \phantomsection\addcontentsline{toc}{chapter}{ACKNOWLEDGMENTS}%
  \ttuleveloneheading{Acknowledgments}\ttubodyspacing}{\clearpage}

\newenvironment{ttuabstract}{%
  \clearpage\phantomsection\addcontentsline{toc}{chapter}{ABSTRACT}%
  \ttuleveloneheading{Abstract}\ttubodyspacing}{\clearpage}

% List of Abbreviations: alphabetized by the author; single-spaced within, body spacing between.
\newenvironment{abbreviations}{%
  \clearpage\phantomsection\addcontentsline{toc}{chapter}{LIST OF ABBREVIATIONS}%
  \ttuleveloneheading{List of Abbreviations}%
  \singlespacing
  \begin{list}{}{\setlength{\labelwidth}{1.4in}\setlength{\leftmargin}{1.6in}\setlength{\labelsep}{0.2in}%
    \setlength{\itemsep}{0.55\baselineskip}\renewcommand{\makelabel}[1]{##1\hfil}}}{\end{list}\clearpage}
\newcommand{\abbrev}[2]{\item[#1] #2}

% ---------- Main matter ----------
\newcommand{\ttumainmatter}{\clearpage\pagenumbering{arabic}\setcounter{page}{1}\pagestyle{ttumain}\ttubodyspacing}

% Optional AI-use declaration to be placed directly under a chapter heading (TTU AI policy)
\newcommand{\aideclaration}[1]{\begingroup\singlespacing\small\noindent\textit{AI-use declaration.} #1\par\endgroup\vspace{8pt}}
% Authorship / publication statement for multi-paper chapters
\newcommand{\authorshipstatement}[1]{\begingroup\singlespacing\small\noindent\textit{Publication note.} #1\par\endgroup\vspace{8pt}}

% ---------- Bibliography (biblatex-ieee): single within entries, body spacing between ----------
\RequirePackage[backend=biber,style=ieee,sorting=none,maxbibnames=10,minbibnames=6,doi=true,url=false,isbn=false,giveninits=true,dashed=false]{biblatex}
\setlength{\bibitemsep}{0.55\baselineskip}
\setlength{\bibhang}{0pt}
\renewcommand*{\bibfont}{\normalfont\normalsize\linespread{1}\selectfont}
\defbibheading{ttubib}{\clearpage\phantomsection\addcontentsline{toc}{chapter}{REFERENCES}\ttuleveloneheading{References}}
\newcommand{\ttureferences}{\begingroup\interlinepenalty=10000\raggedright\printbibliography[heading=ttubib]\endgroup}

% ---------- Appendices: "APPENDIX A" banner + title, floats A.1, in LOT/LOF ----------
\newcommand{\ttuappendices}{%
  \clearpage
  \appendix
  \renewcommand{\thechapter}{\Alph{chapter}}%
  \renewcommand{\thefigure}{\thechapter.\arabic{figure}}%
  \renewcommand{\thetable}{\thechapter.\arabic{table}}%
  \renewcommand{\theequation}{\thechapter.\arabic{equation}}%
  \addtocontents{toc}{\protect\renewcommand{\protect\cftchappresnum}{APPENDIX\space}}%
  \addtocontents{toc}{\protect\setcounter{tocdepth}{0}}% no appendix subheadings in the TOC
}

% ---------- Misc ----------
\RequirePackage{xcolor}
\RequirePackage{enumitem}
\setlist{nosep,leftmargin=*}
% Block quotations single-spaced and indented
\renewenvironment{quote}{\list{}{\rightmargin\leftmargin}\item\relax\singlespacing}{\endlist}
% TODO marker for drafting (prints in draft, invisible otherwise? — keep visible during drafting)
\newcommand{\todo}[1]{\if@ttudraft{\color{red}\textbf{[TODO: #1]}}\else{\color{red!70!black}\textbf{[TODO: #1]}}\fi}

\endinput
