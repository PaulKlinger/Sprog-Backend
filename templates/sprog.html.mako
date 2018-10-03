<!doctype html>

<html lang="en">
<head>
    <meta charset="utf-8">
    <title>The Unofficial Poem_for_your_sprog Collection</title>
    <meta name="author" content="/u/Almoturg">
    <meta name="description" content="A pdf collection of all ${len(poems)} Reddit poems by /u/Poem_for_your_sprog."/>
    <link rel="icon" type="image/png" href="/fleuron.png">
    <link href="https://fonts.googleapis.com/css?family=Patua+One|Roboto" rel="stylesheet">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
<style>
    html, body {
        height: 100%;
        margin:0;
        padding:0;
        overflow: auto;
    }
    body{
        display: flex;
        background-image: url("/bg.jpg");
        background-position: right bottom;
        background-repeat: no-repeat;
        background-size: cover;
        background-attachment: fixed;
    }
    #download {
        display: flex;
        margin-left: auto;
        margin-right: auto;
        max-width: 400px;
        text-align: center;
    }
    #container {
        font-family: 'Roboto', sans-serif;
        background-color: transparent;
        max-width: 650px;
        padding: 40px;
        margin: auto;
        position: relative;
        transform: perspective(1px); /* this fixes artifacts in Edge */
    }
    #blur{
        z-index: -100;
        width: 100%;
        height: 100%;
        position:absolute;
        top:0px;
        right:0px;
        bottom:0px;
        left:0px;
        background-color: rgba(247, 250, 252, 0.8);
        border-radius: 60px;
        box-shadow: 0 0 100px 100px rgba(247, 250, 252, 0.8);
        filter: blur(10px);
    }
    #app {
        max-width: 450px;
        margin-left:auto;
        margin-right: auto;
        padding-top: 50px;
        text-align: center;
        font-size: 15pt;
    }
    #rss {
        max-width: 450px;
        margin-left:auto;
        margin-right: auto;
        padding-top: 50px;
        font-size: 15pt;
        text-align: center;
    }
    .rss_feed {
        display:flex;
        justify-content:center;
        align-items:center;
    }
    .rss_icon {
        width: 30px;
        height: 30px;
    }
    #playstore {
        width: 12em;
    }
    #stats {
        max-width: 450px;
        margin-left:auto;
        margin-right: auto;
        padding-top: 20px;
        padding-bottom: 50px;
        text-align: center;
    }
    #stats ul {padding: 0;}
    #stats li:before {
        background-image: url("/fleuron.png");
        background-size: 1.1em 1.1em;
        background-repeat: no-repeat;
        background-position: center;
        height: 1.2em;
        position: relative;
        bottom: 8px;
        text-align: center;
        width: 100%;
        display: block;
        content: " ";
    }
    #stats li:first-child:before{
      display: none;
    }
    #stats li {
        font-size: 15pt;
        margin-top: 0.8em;
        list-style: none;
    }
    #title {
        text-align: center;
        font-family: 'Patua One', cursive;
    }
    .button {
        margin: auto;
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        font-size: 16px;
    }
    #download_button {
        background-color: #4CAF50; /* Green */
    }
    #mobile_download_button {
        background-color: #3B8386; /* Blue */
    }
    #updated {
        font-size: 10pt;
        color: #b1b5bc;
        padding-top:1em;
        text-align:center;
    }
    h1 {
        font-size: 30pt;
        color: #313233;
        line-height: 1.3;
        font-weight: normal;
    }
    #author {
        font-size:20pt;
        color: #b1b5bc;
        font-weight: normal;
    }

    #updated a {
        color: #999;
    }

    @media screen and (max-width: 500px) {
        #body {background-attachment: scroll;}
        #container {
            width: 90vw;
            padding: 0;
            padding-left: 5vw;
            padding-right: 5vw;
        }
        h1 {font-size: 20pt}
        #author {font-size: 15pt}
        #stats li {font-size: 12pt}
        .button {
            font-size: 13pt;
            margin-bottom: 2em;
        }
        #download {flex-wrap: wrap-reverse;}
        #stats {padding-top: 25px; padding-bottom: 25px;}
        #blur {box-shadow: 0 0 100px 30px rgba(247, 250, 252, 0.8);}
    }
    @media screen and (max-width: 350px) {
        h1 {font-size: 18pt}
        #author {font-size: 14pt}

    }
</style>

<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-133792-3', 'auto');
  ga('send', 'pageview');

</script>
</head>

<body>
    <div id="container">
        <div id="blur">
        </div>
        <div id="title">
        <h1>The Unofficial<br/>

            /u/Poem_for_your_sprog<br/>

            Collection<br/>
            <span id="author">by /u/Almoturg</span>
            </h1>
        </div>
        <div id="rss">
            RSS feeds now available! <br />
            <a class="rss_feed" href="sprog.rss"><img class="rss_icon" src="rss_icon.png"/>RSS feed of poems with context</a>
            <a class="rss_feed" href="sprog_no_context.rss"><img class="rss_icon" src="rss_icon.png"/>RSS feed of just the poems</a>
        </div>
        <div id="app">
            Get the free Android app:<br />
            <a href='http://play.google.com/store/apps/details?id=com.almoturg.sprog&utm_source=website&pcampaignid=MKT-Other-global-all-co-prtnr-py-PartBadge-Mar2515-1'>
                <img id="playstore" alt='Get it on Google Play' src='https://play.google.com/intl/en_us/badges/images/generic/en_badge_web_generic.png'/>
            </a>
        </div>
        <div id="stats">
            <ul>
                <li>Containing ${len(poems)} poems on ${pages} / ${pages_small} pages.</li>
                <li>From ${suffix_strftime("%B {S}, %Y", poems[-1].datetime)}
                    to ${suffix_strftime("%B {S}, %Y", poems[0].datetime)}.</li>
            </ul>
        </div>
        <div id="download">
            <a href="/sprog.pdf" id="download_button" class="button"
               onclick="ga('send', 'event',
                        {eventCategory: 'download',
                         eventAction: 'click',
                         eventLabel: 'pdf downloaded',
                         transport: 'beacon'});">
                full-size pdf<br/>
                (for desktop/print)
            </a>
            <a href="/sprog_small.pdf" id="mobile_download_button" class="button"
               onclick="ga('send', 'event',
                        {eventCategory: 'download',
                         eventAction: 'click',
                         eventLabel: 'mobile pdf downloaded',
                         transport: 'beacon'});">
                small pdf<br/>
                (for mobile)
            </a>
        </div>
        <div id="updated">
            last updated ${now.strftime("%Y-%m-%d %H:%M:%S")} (UTC)<br/>
            next scheduled update ${next_update.strftime("%Y-%m-%d %H:%M:%S")} (UTC).<br/>
            Code available on <a href="https://github.com/PaulKlinger">GitHub</a>
            for <a href="https://github.com/PaulKlinger/Sprog-Backend">backend</a>
            and <a href="https://github.com/PaulKlinger/Sprog-App">app</a>.<br/>
            Google Play and the Google Play logo are trademarks of Google Inc.
        </div>
    </div>

</body>
</html>