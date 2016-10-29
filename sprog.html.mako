<!doctype html>

<html lang="en">
<head>
    <meta charset="utf-8">
    <title>The unofficial Poem_for_your_sprog Collection</title>
    <meta name="author" content="/u/Almoturg">
    <link rel="icon" type="image/png" href="fleuron.png">
    <link href="https://fonts.googleapis.com/css?family=Patua+One|Roboto" rel="stylesheet">
<style>
    html, body {
        height: 100%;
        margin:0;
        padding:0;
    }
    body{
        background-image: url("bg.jpg");
        background-position: right bottom;
        background-repeat: no-repeat;
        background-size: cover;
    }
    #download {
        margin-left: auto;
        margin-right: auto;
        display: block;
        width:200px;
        height:30px;
        text-align: center;
    }
    #container {
        box-shadow: 0 0 100px 100px rgba(247, 250, 252, 0.8);
        font-family: 'Roboto', sans-serif;
        background-color: rgba(247, 250, 252, 0.8);
        border-radius: 60px;
        max-width: 650px;
        padding: 40px;
        margin-left:auto;
        margin-right:auto;
        /* the stuff below is for vertical centering */
        position: relative;
        top: 50%;
        transform: perspective(1px) translateY(-50%); /* the perspective thingy prevents some artifacts/blurryness */
    }
    #stats {
        max-width: 450px;
        margin-left:auto;
        margin-right: auto;
        padding-top: 50px;
        padding-bottom: 50px;
        text-align: center;
    }
    #stats ul {padding: 0;}
    #stats li:before {
        background-image: url('fleuron.png');
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
    #download_button {
        background-color: #4CAF50; /* Green */
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
    }
    h1 {
        font-size: 30pt;
        color: #313233;
        line-height: 1.3;
        font-weight: normal;
    }
    h2 {
        font-size:20pt;
        color: #b1b5bc;
        font-weight: normal;
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
        <div id="title">
        <h1>The Unofficial<br/>

            /u/Poem_for_your_sprog<br/>

            Collection</h1>
            <h2>by /u/Almoturg</h2>
        </div>
        <div id="stats">
            <ul>
                <li>Containing ${len(poems)} poems on ${pages} pages.</li>
                <li>From ${suffix_strftime("%B {S}, %Y", poems[-1].datetime)}
                    to ${suffix_strftime("%B {S}, %Y", poems[0].datetime)}.</li>
            </ul>
        </div>
        <div id="download">
            <a href="sprog.pdf" id="download_button">Get the .pdf!</a>
        </div>
    </div>

</body>
</html>