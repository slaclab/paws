<!DOCTYPE html>
<html lang="en">
<head>
  
  
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <meta charset="utf-8">
  <title>
  smashml / slacx 
  / source  / core / workflow / slacxwfman.py
 &mdash; Bitbucket
</title>
  <script type="text/javascript">window.NREUM||(NREUM={}),__nr_require=function(t,e,n){function r(n){if(!e[n]){var o=e[n]={exports:{}};t[n][0].call(o.exports,function(e){var o=t[n][1][e];return r(o||e)},o,o.exports)}return e[n].exports}if("function"==typeof __nr_require)return __nr_require;for(var o=0;o<n.length;o++)r(n[o]);return r}({1:[function(t,e,n){function r(){}function o(t,e,n){return function(){return i(t,[(new Date).getTime()].concat(u(arguments)),e?null:this,n),e?void 0:this}}var i=t("handle"),a=t(2),u=t(3),c=t("ee").get("tracer"),f=NREUM;"undefined"==typeof window.newrelic&&(newrelic=f);var s=["setPageViewName","setCustomAttribute","setErrorHandler","finished","addToTrace","inlineHit"],p="api-",l=p+"ixn-";a(s,function(t,e){f[e]=o(p+e,!0,"api")}),f.addPageAction=o(p+"addPageAction",!0),e.exports=newrelic,f.interaction=function(){return(new r).get()};var d=r.prototype={createTracer:function(t,e){var n={},r=this,o="function"==typeof e;return i(l+"tracer",[Date.now(),t,n],r),function(){if(c.emit((o?"":"no-")+"fn-start",[Date.now(),r,o],n),o)try{return e.apply(this,arguments)}finally{c.emit("fn-end",[Date.now()],n)}}}};a("setName,setAttribute,save,ignore,onEnd,getContext,end,get".split(","),function(t,e){d[e]=o(l+e)}),newrelic.noticeError=function(t){"string"==typeof t&&(t=new Error(t)),i("err",[t,(new Date).getTime()])}},{}],2:[function(t,e,n){function r(t,e){var n=[],r="",i=0;for(r in t)o.call(t,r)&&(n[i]=e(r,t[r]),i+=1);return n}var o=Object.prototype.hasOwnProperty;e.exports=r},{}],3:[function(t,e,n){function r(t,e,n){e||(e=0),"undefined"==typeof n&&(n=t?t.length:0);for(var r=-1,o=n-e||0,i=Array(o<0?0:o);++r<o;)i[r]=t[e+r];return i}e.exports=r},{}],ee:[function(t,e,n){function r(){}function o(t){function e(t){return t&&t instanceof r?t:t?u(t,a,i):i()}function n(n,r,o){t&&t(n,r,o);for(var i=e(o),a=l(n),u=a.length,c=0;c<u;c++)a[c].apply(i,r);var s=f[m[n]];return s&&s.push([w,n,r,i]),i}function p(t,e){g[t]=l(t).concat(e)}function l(t){return g[t]||[]}function d(t){return s[t]=s[t]||o(n)}function v(t,e){c(t,function(t,n){e=e||"feature",m[n]=e,e in f||(f[e]=[])})}var g={},m={},w={on:p,emit:n,get:d,listeners:l,context:e,buffer:v};return w}function i(){return new r}var a="nr@context",u=t("gos"),c=t(2),f={},s={},p=e.exports=o();p.backlog=f},{}],gos:[function(t,e,n){function r(t,e,n){if(o.call(t,e))return t[e];var r=n();if(Object.defineProperty&&Object.keys)try{return Object.defineProperty(t,e,{value:r,writable:!0,enumerable:!1}),r}catch(i){}return t[e]=r,r}var o=Object.prototype.hasOwnProperty;e.exports=r},{}],handle:[function(t,e,n){function r(t,e,n,r){o.buffer([t],r),o.emit(t,e,n)}var o=t("ee").get("handle");e.exports=r,r.ee=o},{}],id:[function(t,e,n){function r(t){var e=typeof t;return!t||"object"!==e&&"function"!==e?-1:t===window?0:a(t,i,function(){return o++})}var o=1,i="nr@id",a=t("gos");e.exports=r},{}],loader:[function(t,e,n){function r(){if(!h++){var t=y.info=NREUM.info,e=s.getElementsByTagName("script")[0];if(t&&t.licenseKey&&t.applicationID&&e){c(m,function(e,n){t[e]||(t[e]=n)});var n="https"===g.split(":")[0]||t.sslForHttp;y.proto=n?"https://":"http://",u("mark",["onload",a()],null,"api");var r=s.createElement("script");r.src=y.proto+t.agent,e.parentNode.insertBefore(r,e)}}}function o(){"complete"===s.readyState&&i()}function i(){u("mark",["domContent",a()],null,"api")}function a(){return(new Date).getTime()}var u=t("handle"),c=t(2),f=window,s=f.document,p="addEventListener",l="attachEvent",d=f.XMLHttpRequest,v=d&&d.prototype;NREUM.o={ST:setTimeout,CT:clearTimeout,XHR:d,REQ:f.Request,EV:f.Event,PR:f.Promise,MO:f.MutationObserver},t(1);var g=""+location,m={beacon:"bam.nr-data.net",errorBeacon:"bam.nr-data.net",agent:"js-agent.newrelic.com/nr-974.min.js"},w=d&&v&&v[p]&&!/CriOS/.test(navigator.userAgent),y=e.exports={offset:a(),origin:g,features:{},xhrWrappable:w};s[p]?(s[p]("DOMContentLoaded",i,!1),f[p]("load",r,!1)):(s[l]("onreadystatechange",o),f[l]("onload",r)),u("mark",["firstbyte",a()],null,"api");var h=0},{}]},{},["loader"]);</script>
  


<meta id="bb-canon-url" name="bb-canon-url" content="https://bitbucket.org">

<meta name="bb-view-name" content="bitbucket.apps.repo2.views.filebrowse">
<meta name="ignore-whitespace" content="False">
<meta name="tab-size" content="None">

<meta name="application-name" content="Bitbucket">
<meta name="apple-mobile-web-app-title" content="Bitbucket">
<meta name="theme-color" content="#205081">
<meta name="msapplication-TileColor" content="#205081">
<meta name="msapplication-TileImage" content="https://d301sr5gafysq2.cloudfront.net/4729d131423b/img/logos/bitbucket/white-256.png">
<link rel="apple-touch-icon" sizes="192x192" type="image/png" href="https://d301sr5gafysq2.cloudfront.net/4729d131423b/img/bitbucket_avatar/192/bitbucket.png">
<link rel="icon" sizes="192x192" type="image/png" href="https://d301sr5gafysq2.cloudfront.net/4729d131423b/img/bitbucket_avatar/192/bitbucket.png">
<link rel="icon" sizes="16x16 32x32" type="image/x-icon" href="/favicon.ico">
<link rel="search" type="application/opensearchdescription+xml" href="/opensearch.xml" title="Bitbucket">
  <meta name="description" content="">
  
  
    
  



  <link rel="stylesheet" href="https://d301sr5gafysq2.cloudfront.net/4729d131423b/css/entry/vendor.css" />
<link rel="stylesheet" href="https://d301sr5gafysq2.cloudfront.net/4729d131423b/css/entry/app.css" />




  
  <script src="https://d301sr5gafysq2.cloudfront.net/4729d131423b/dist/webpack/early.js"></script>
  
  
  
    <link href="/smashml/slacx/rss?token=2b493e1ad6e589122eb16e4fec098e7b" rel="alternate nofollow" type="application/rss+xml" title="RSS feed for slacx" />

</head>
<body class="production aui-page-sidebar aui-sidebar-collapsed"
    data-static-url="https://d301sr5gafysq2.cloudfront.net/4729d131423b/"
data-base-url="https://bitbucket.org"
data-base-api-url="https://api.bitbucket.org"
data-no-avatar-image="https://d301sr5gafysq2.cloudfront.net/4729d131423b/img/default_avatar/user_blue.svg"
data-current-user="{&quot;username&quot;: &quot;lensonp&quot;, &quot;displayName&quot;: &quot;Lenson Pellouchoud&quot;, &quot;uuid&quot;: &quot;{d72dcb53-7f54-475d-a9c3-acbafdf39c90}&quot;, &quot;firstName&quot;: &quot;Lenson Pellouchoud&quot;, &quot;avatarUrl&quot;: &quot;https://bitbucket.org/account/lensonp/avatar/32/?ts=1476219911&quot;, &quot;lastName&quot;: &quot;&quot;, &quot;isTeam&quot;: false, &quot;isSshEnabled&quot;: true, &quot;isKbdShortcutsEnabled&quot;: true, &quot;id&quot;: 7520975, &quot;isAuthenticated&quot;: true}"
data-atlassian-id="{&quot;loginStatusUrl&quot;: &quot;https://id.atlassian.com/profile/rest/profile&quot;}"
data-settings="{&quot;MENTIONS_MIN_QUERY_LENGTH&quot;: 3}"

data-current-repo="{&quot;scm&quot;: &quot;git&quot;, &quot;readOnly&quot;: false, &quot;mainbranch&quot;: {&quot;name&quot;: &quot;master&quot;}, &quot;language&quot;: &quot;&quot;, &quot;owner&quot;: {&quot;username&quot;: &quot;smashml&quot;, &quot;uuid&quot;: &quot;1bb2e660-a974-4d01-bfe6-e19060aea79a&quot;, &quot;isTeam&quot;: true}, &quot;fullslug&quot;: &quot;smashml/slacx&quot;, &quot;slug&quot;: &quot;slacx&quot;, &quot;id&quot;: 20474718, &quot;pygmentsLanguage&quot;: null}"
data-current-cset="5b763e8d612ceca1e84b0ef52fd4cc673fd4e82a"





data-browser-monitoring="true"
data-switch-create-pullrequest-commit-status="true"


>
<div id="page">
  
    <ak-page
      
        navigation-open
      
    >
      
    
    <div id="wrapper">
      
  


      
        <header id="header" role="banner" data-module="header/tracking">
          
  


          <nav class="aui-header aui-dropdown2-trigger-group" role="navigation">
            <div class="aui-header-inner">
              <div class="aui-header-primary">
                
  
  <div class="aui-header-before">
    <button class="app-switcher-trigger aui-dropdown2-trigger aui-dropdown2-trigger-arrowless" aria-controls="app-switcher" aria-haspopup="true" tabindex="0"
    
        data-nav-links-count="0"
    
    >
      <span class="aui-icon aui-icon-small aui-iconfont-appswitcher">Linked applications</span>
    </button>
    
      <nav id="app-switcher" class="aui-dropdown2 aui-style-default">
        <div class="aui-dropdown2-section blank-slate">
          <h2>Connect Bitbucket with other great Atlassian products:</h2>
          <dl>
            <dt class="jira">JIRA</dt>
            <dd>Project and issue tracking</dd>
            <dt class="confluence">Confluence</dt>
            <dd>Collaboration and content sharing</dd>
            <dt class="bamboo">Bamboo</dt>
            <dd>Continuous integration</dd>
          </dl>
          <ul>
            <li>
              <a href="https://www.atlassian.com/ondemand/signup/?product=jira.ondemand,com.atlassian.bitbucket&utm_source=bitbucket&utm_medium=button&utm_campaign=app_switcher&utm_content=trial_button"
                 class="aui-button aui-button-primary" target="_blank" id="ondemand-trial" data-ct="header.app.switcher.dropdown.trial">Free trial</a>
            </li>
            <li>
              <a href="https://www.atlassian.com/software?utm_source=bitbucket&utm_medium=button&utm_campaign=app_switcher&utm_content=learn_more_button#cloud-products"
                 class="aui-button" target="_blank" id="ondemand-learn-more" data-ct="header.app.switcher.dropdown.learnmore">Learn more</a>
            </li>
          </ul>
        </div>
      </nav>
    
  </div>


                
                  <h1 class="aui-header-logo aui-header-logo-bitbucket "
                      id="logo" data-ct="header.logo">
                    <a href="/">
                      <span class="aui-header-logo-device">Bitbucket</span>
                    </a>
                  </h1>
                
                
  

    <script id="repo-dropdown-template" type="text/html">
      


  [[#hasViewed]]
    <div class="aui-dropdown2-section">
      <strong class="viewed">Recently viewed</strong>
      <ul>
        [[#viewed]]
          <li class="[[#is_private]]private[[/is_private]][[^is_private]]public[[/is_private]] repository">
            <a href="[[url]]" title="[[owner]][[#project]] / [[project]][[/project]] / [[name]]" class="aui-icon-container recently-viewed repo-link"
                data-ct="header.repository.dropdown.repository" data-ct-data='{"type": "recently-viewed"}'>
              <span class="aui-avatar aui-avatar-xsmall aui-avatar-project">
                <span class="aui-avatar-inner">
                  <img src="[[{avatar}]]">
                </span>
              </span>
              <span class="dropdown-path">
                <span class="dropdown-path-part">[[#project]][[project]][[/project]][[^project]][[owner]][[/project]]</span>
                <span class="dropdown-path-separator">/</span>
                <span class="dropdown-path-part dropdown-path-part--primary">[[name]]</span>
              </span>
            </a>
          </li>
        [[/viewed]]
      </ul>
    </div>
  [[/hasViewed]]
  [[#hasUpdated]]
    <div class="aui-dropdown2-section">
      <strong class="updated">Recently updated</strong>
      <ul>
        [[#updated]]
        <li class="[[#is_private]]private[[/is_private]][[^is_private]]public[[/is_private]] repository">
          <a href="[[url]]" title="[[owner]][[#project]] / [[project]][[/project]] / [[name]]" class="aui-icon-container recently-updated repo-link"
             data-ct="header.repository.dropdown.repository" data-ct-data='{"type": "recently-updated"}'>
            <span class="aui-avatar aui-avatar-xsmall aui-avatar-project">
              <span class="aui-avatar-inner">
                <img src="[[{avatar}]]">
              </span>
            </span>
            <span class="dropdown-path">
              <span class="dropdown-path-part">[[#project]][[project]][[/project]][[^project]][[owner]][[/project]]</span>
              <span class="dropdown-path-separator">/</span>
              <span class="dropdown-path-part dropdown-path-part--primary">[[name]]</span>
            </span>
          </a>
        </li>
        [[/updated]]
      </ul>
    </div>
  [[/hasUpdated]]


    </script>
  

    <script id="snippet-dropdown-template" type="text/html">
      <div class="aui-dropdown2-section">
  <strong>[[sectionTitle]]</strong>
  <ul class="aui-list-truncate">
    [[#snippets]]
      <li>
        <a href="[[links.html.href]]">[[owner.display_name]] / [[name]]</a>
      </li>
    [[/snippets]]
  </ul>
</div>

    </script>
  
<ul class="aui-nav">
  
    <li>
      
    <script id="team-dropdown-template" type="text/html">
      

<div class="aui-dropdown2-section primary">
  <ul class="aui-list-truncate">
    [[#teams]]
      <li>
        <a href="/[[username]]/" class="aui-icon-container team-link" data-ct="header.team.dropdown.team">
          <span class="aui-avatar aui-avatar-xsmall">
            <span class="aui-avatar-inner">
              <img src="[[avatar]]">
            </span>
          </span>
          [[display_name]]
        </a>
      </li>
    [[/teams]]
  </ul>
</div>

<div class="aui-dropdown2-section">
  <ul>
    <li>
      <a href="/account/create-team/?team_source=header"
          id="create-team-link" data-ct="header.team.dropdown.create" data-ct-data='{"empty": false}'>Create team</a>
    </li>
  </ul>
</div>

    </script>
  
      <a class="aui-dropdown2-trigger" href="#teams-dropdown" id="teams-dropdown-trigger"
          data-module="header/teams-dropdown"
          aria-owns="teams-dropdown" aria-haspopup="true">
        Teams
        <span class="aui-icon-dropdown"></span>
      </a>
      <div id="teams-dropdown" class="aui-dropdown2 aui-style-default">
        <div class="aui-dropdown2-section nav-dropdown--blank-state">
          <p>
            Effective collaboration starts with teams and projects.
          </p>
          <ul>
            <li>
              <a class="aui-button aui-button-link nav-dropdown--blank-state--cta nav-dropdown--blank-state--link" id="create-team-blank-slate"
                  data-ct="header.team.dropdown.create" data-ct-data='{"empty": true}'
                  href="/account/create-team/?team_source=menu_blank"
                  >Create a team</a>
            </li>
          </ul>
        </div>
      </div>
    </li>
    <li>
      
    <script id="projects-dropdown-template" type="text/html">
      

[[#hasProjects]]
  <div class="aui-dropdown2-section">
    <strong>Recently viewed</strong>
    <ul class="aui-list-truncate">
      [[#projects]]
        <li>
          <a href="/account/user/[[owner.username]]/projects/[[key]]" class="aui-icon-container project-link">
            <span class="aui-avatar aui-avatar-xsmall aui-avatar-project">
              <span class="aui-avatar-inner">
                <img src="[[links.avatar.href]]">
              </span>
            </span>
            [[name]]
          </a>
        </li>
      [[/projects]]
    </ul>
  </div>
[[/hasProjects]]

[[#isAdmin]]
  <div class="aui-dropdown2-section">
    <ul>
      <li>
        <a href="/account/projects/create"
            id="create-project-link">Create project</a>
      </li>
    </ul>
  </div>
[[/isAdmin]]

    </script>
  
      <a class="aui-dropdown2-trigger" href="#teams-dropdown" id="projects-dropdown-trigger"
          data-module="header/projects-dropdown"
          aria-owns="projects-dropdown" aria-haspopup="true">
        Projects
        <span class="aui-icon-dropdown"></span>
      </a>
      <div id="projects-dropdown" class="aui-dropdown2 aui-style-default">
        <div class="aui-dropdown2-section nav-dropdown--blank-state">
          <p>
            
              Get a team, get projects, get organized.
            
          </p>
          <ul>
            <li>
              <a class="aui-button aui-button-link nav-dropdown--blank-state--cta nav-dropdown--blank-state--link" id="projects-create-team-blank-slate"
                  href="/account/create-team/?team_source=menu_blank"
                  >Create a team</a>
            </li>
          </ul>
        </div>
      </div>
    </li>
    <li>
      <a class="aui-dropdown2-trigger" id="repositories-dropdown-trigger"
          aria-owns="repo-dropdown" aria-haspopup="true" href="/repo/mine">
        Repositories
        <span class="aui-icon-dropdown"></span>
      </a>
      <nav id="repo-dropdown" class="aui-dropdown2 aui-style-default">
        <div id="repo-dropdown-recent" data-module="header/recent-repos"></div>
        <div class="aui-dropdown2-section">
          <ul>
            <li>
              <a href="/repo/create" class="new-repository" id="create-repo-link" data-ct="header.repository.dropdown.create">
                Create repository
              </a>
            </li>
            <li>
              <a href="/repo/import" class="import-repository" id="import-repo-link" data-ct="header.repository.dropdown.import">
                Import repository
              </a>
            </li>
          </ul>
        </div>
      </nav>
    </li>
    <li>
      <a class="aui-dropdown2-trigger" id="snippets-dropdown-trigger"
        aria-owns="nav-recent-snippets" aria-haspopup="true" href="/snippets/">
        Snippets
        <span class="aui-icon-dropdown"></span>
      </a>
      <nav id="nav-recent-snippets" class="aui-dropdown2 aui-style-default">
        <div id="snippet-dropdown-recent" class="aui-dropdown2-section"
            data-module="snippets/recent-list"></div>
        <div class="aui-dropdown2-section">
          <ul>
            <li>
              <a href="/snippets/new" data-ct="header.snippets.dropdown.create">
                Create snippet
              </a>
            </li>
          </ul>
        </div>
      </nav>
    </li>
  
</ul>

              </div>
              <div class="aui-header-secondary">
                
  

<ul role="menu" class="aui-nav">
  
  <li>
    <form action="/repo/all" method="get" class="aui-quicksearch">
      <label for="search-query" class="assistive">owner/repository</label>
      <input id="search-query" class="bb-repo-typeahead" type="text"
             placeholder="Find a repository&hellip;" name="name" autocomplete="off"
             data-bb-typeahead-focus="false">
    </form>
  </li>
  <li>
    <a id="help-menu-link" class="aui-nav-link" href="#"
        aria-controls="help-menu-dialog"
        data-aui-trigger>
      <span id="help-menu-icon" class="aui-icon aui-icon-small aui-iconfont-help"></span>
    </a>
  </li>
  
  
    <li>
      <a class="aui-dropdown2-trigger aui-dropdown2-trigger-arrowless"
         aria-owns="user-dropdown" aria-haspopup="true" data-container="#header .aui-header-inner"
         href="/lensonp/" title="lensonp" id="user-dropdown-trigger">
        <div class="aui-avatar aui-avatar-small">
            <div class="aui-avatar-inner">
                <img src="https://d301sr5gafysq2.cloudfront.net/4729d131423b/img/default_avatar/user_blue.svg" class="deferred-image" data-src-url="https://bitbucket.org/account/lensonp/avatar/32/?ts=1476219911" data-src-url-2x="https://bitbucket.org/account/lensonp/avatar/64/?ts=1476219911" alt="Logged in as lensonp" height="24" width="24">
            </div>
        </div>
      </a>
      <nav id="user-dropdown" class="aui-dropdown2 aui-style-default" aria-hidden="true">
        <div class="aui-dropdown2-section">
          <div class="aid-profile">
            <div class="aui-avatar aui-avatar-large">
              <div class="aui-avatar-inner">

                
                  
                

                <a class="aid-profile--change-avatar hoverable" target="_blank" href="https://id.atlassian.com/profile/profile.action#edit-avatar">
                  <span class="hoverable--overlay">
                    <span class="aui-icon aui-icon-large aid-profile--avatar-icon"></span>
                  </span>
                  <img src="https://d301sr5gafysq2.cloudfront.net/4729d131423b/img/default_avatar/user_blue.svg" class="deferred-image" data-src-url="https://bitbucket.org/account/lensonp/avatar/48/?ts=1476219911" data-src-url-2x="https://bitbucket.org/account/lensonp/avatar/96/?ts=1476219911" height="48" width="48">
                </a>
            </div>
          </div>
          <div class="aid-profile--info">
            <div class="aid-profile--name">
              Lenson Pellouchoud
            </div>
            <div class="aid-profile--email">
              lenson@slac.stanford.edu
            </div>
          </div>
        </div>
          
            <ul>
              <li>
                <a href="https://id.atlassian.com/profile" id="account-link" target="_blank" data-ct="navbar.dropdown.manage_aid_account">Manage Atlassian account</a>
              </li>
            </ul>
          
        </div>
        <div class="aui-dropdown2-section">
          <ul>
            <li>
              <a href="/lensonp/" id="profile-link">View profile</a>
            </li>
            <li>
              <a href="/account/user/lensonp/" id="account-link" data-ct="navbar.dropdown.manage_account">Bitbucket settings</a>
            </li>
            <li>
              <a href="/account/user/lensonp/addon-directory" id="account-addons" data-ct="navbar.dropdown.addons">Integrations</a>
            </li>
            
              <li>
                <a href="/account/notifications/" id="inbox-link">Inbox</a>
              </li>
            
          </ul>
        </div>
        <div class="aui-dropdown2-section">
          <ul>
            <li>
              
                <a href="https://id.atlassian.com/logout?continue=https%3A%2F%2Fbitbucket.org%2Faccount%2Fsignout%2F" id="log-out-link">Log out</a>
              
            </li>
          </ul>
        </div>
      </nav>
    </li>
    
      <li id="nps-survey-container"></li>
    
  
</ul>

              </div>
            </div>
          </nav>
        </header>
      

      
  

<header id="account-warning" role="banner" data-module="header/account-warning"
        class="aui-message-banner warning
        ">
  <div class="aui-message-banner-inner">
    <span class="aui-icon aui-icon-warning"></span>
    <span class="message">
    
    </span>
  </div>
</header>



      
  
<header id="aui-message-bar">
  
</header>


    <div id="content" role="main">
      
        
  
    <div class="aui-sidebar repo-sidebar"
    data-module="repo/sidebar"
   aria-expanded="false">
  <div class="aui-sidebar-wrapper">
    <div class="aui-sidebar-body">
      <header class="aui-page-header">
        <div class="aui-page-header-inner">
          <div class="aui-page-header-image">
            <a href="/smashml/slacx" id="repo-avatar-link" class="repo-link">
              <span class="aui-avatar aui-avatar-large aui-avatar-project">
                <span class="aui-avatar-inner">
                  <img src="https://d301sr5gafysq2.cloudfront.net/4729d131423b/img/repo-avatars/default.svg" alt="">
                </span>
              </span>
            </a>
          </div>
          <div class="aui-page-header-main">
            <h1>
              
                <span class="aui-icon aui-icon-small aui-iconfont-locked"></span>
              
              <a href="/smashml/slacx" title="slacx" class="entity-name">slacx</a>
            </h1>
          </div>
        </div>
      </header>
      <nav class="aui-navgroup aui-navgroup-vertical">
        <div class="aui-navgroup-inner">
          
            
              <div class="aui-sidebar-group aui-sidebar-group-actions repository-actions forks-enabled can-create">
                <div class="aui-nav-heading">
                  <strong>Actions</strong>
                </div>
                <ul id="repo-actions" class="aui-nav">
                  
                  
                    <li>
                      <a id="repo-clone-button" class="aui-nav-item "
                        href="#clone"
                        data-ct="sidebar.actions.repository.clone"
                        data-ct-data=""
                        data-module="components/clone/clone-dialog"
                        target="_self">
                        
                          <span class="aui-icon aui-icon-large icon-clone"></span>
                        
                        <span class="aui-nav-item-label">Clone</span>
                      </a>
                    </li>
                  
                    <li>
                      <a id="repo-create-branch-link" class="aui-nav-item create-branch-button"
                        href="/smashml/slacx/branch"
                        data-ct="sidebar.actions.repository.create_branch"
                        data-ct-data=""
                        data-module="repo/create-branch"
                        target="_self">
                        
                          <span class="aui-icon aui-icon-large icon-create-branch"></span>
                        
                        <span class="aui-nav-item-label">Create branch</span>
                      </a>
                    </li>
                  
                    <li>
                      <a id="repo-create-pull-request-link" class="aui-nav-item "
                        href="/smashml/slacx/pull-requests/new"
                        data-ct="sidebar.actions.create_pullrequest"
                        data-ct-data=""
                        
                        target="_self">
                        
                          <span class="aui-icon aui-icon-large icon-create-pull-request"></span>
                        
                        <span class="aui-nav-item-label">Create pull request</span>
                      </a>
                    </li>
                  
                    <li>
                      <a id="repo-compare-link" class="aui-nav-item "
                        href="/smashml/slacx/branches/compare"
                        data-ct="sidebar.actions.repository.compare"
                        data-ct-data=""
                        
                        target="_self">
                        
                          <span class="aui-icon aui-icon-large aui-icon-small aui-iconfont-devtools-compare"></span>
                        
                        <span class="aui-nav-item-label">Compare</span>
                      </a>
                    </li>
                  
                    <li>
                      <a id="repo-fork-link" class="aui-nav-item "
                        href="/smashml/slacx/fork"
                        data-ct="sidebar.actions.repository.fork"
                        data-ct-data=""
                        
                        target="_self">
                        
                          <span class="aui-icon aui-icon-large icon-fork"></span>
                        
                        <span class="aui-nav-item-label">Fork</span>
                      </a>
                    </li>
                  
                </ul>
              </div>
          
          <div class="aui-sidebar-group aui-sidebar-group-tier-one repository-sections">
            <div class="aui-nav-heading">
              <strong>Navigation</strong>
            </div>
            <ul class="aui-nav">
              
              
                <li>
                  <a id="repo-overview-link" class="aui-nav-item "
                    href="/smashml/slacx/overview"
                    data-ct="sidebar.navigation.repository.overview"
                    data-ct-data=""
                    
                    target="_self"
                    >
                    
                    
                      <span class="aui-icon aui-icon-large icon-overview"></span>
                    
                    <span class="aui-nav-item-label">
                      Overview
                      
                      
                    </span>
                  </a>
                </li>
              
                <li class="aui-nav-selected">
                  <a id="repo-source-link" class="aui-nav-item "
                    href="/smashml/slacx/src"
                    data-ct="sidebar.navigation.repository.source"
                    data-ct-data=""
                    
                    target="_self"
                    >
                    
                    
                      <span class="aui-icon aui-icon-large icon-source"></span>
                    
                    <span class="aui-nav-item-label">
                      Source
                      
                      
                    </span>
                  </a>
                </li>
              
                <li>
                  <a id="repo-commits-link" class="aui-nav-item "
                    href="/smashml/slacx/commits/"
                    data-ct="sidebar.navigation.repository.commits"
                    data-ct-data=""
                    
                    target="_self"
                    >
                    
                    
                      <span class="aui-icon aui-icon-large icon-commits"></span>
                    
                    <span class="aui-nav-item-label">
                      Commits
                      
                      
                    </span>
                  </a>
                </li>
              
                <li>
                  <a id="repo-branches-link" class="aui-nav-item "
                    href="/smashml/slacx/branches/"
                    data-ct="sidebar.navigation.repository.branches"
                    data-ct-data=""
                    
                    target="_self"
                    >
                    
                    
                      <span class="aui-icon aui-icon-large icon-branches"></span>
                    
                    <span class="aui-nav-item-label">
                      Branches
                      
                      
                    </span>
                  </a>
                </li>
              
                <li>
                  <a id="repo-pullrequests-link" class="aui-nav-item "
                    href="/smashml/slacx/pull-requests/"
                    data-ct="sidebar.navigation.repository.pullrequests"
                    data-ct-data=""
                    
                    target="_self"
                    >
                    
                    
                      <span class="aui-icon aui-icon-large icon-pull-requests"></span>
                    
                    <span class="aui-nav-item-label">
                      Pull requests
                      
                      
                    </span>
                  </a>
                </li>
              
                <li>
                  <a id="repo-downloads-link" class="aui-nav-item "
                    href="/smashml/slacx/downloads"
                    data-ct="sidebar.navigation.repository.downloads"
                    data-ct-data=""
                    
                    target="_self"
                    >
                    
                    
                      <span class="aui-icon aui-icon-large icon-downloads"></span>
                    
                    <span class="aui-nav-item-label">
                      Downloads
                      
                      
                    </span>
                  </a>
                </li>
              
            </ul>
          </div>
          <div class="aui-sidebar-group aui-sidebar-group-tier-one repository-settings">
            <div class="aui-nav-heading">
              <strong class="assistive">Settings</strong>
            </div>
            <ul class="aui-nav">
              
              
                <li>
                  <a id="repo-settings-link" class="aui-nav-item "
                    href="/smashml/slacx/admin"
                    
                    target="_self"
                    >
                    
                    <span class="aui-icon aui-icon-large icon-settings"></span>
                    <span class="aui-nav-item-label">Settings</span>
                  </a>
                </li>
              
            </ul>
          </div>
          
        </div>
      </nav>
    </div>
    <div class="aui-sidebar-footer">
      <a class="aui-sidebar-toggle aui-sidebar-footer-tipsy aui-button aui-button-subtle"><span class="aui-icon"></span></a>
    </div>
  </div>
  

<div id="repo-clone-dialog" class="clone-dialog hidden">
  





  

<div class="clone-url" data-module="components/clone/url-dropdown" data-owner="1bb2e660-a974-4d01-bfe6-e19060aea79a"
     data-location-context="header"
     data-fetch-url="https://lensonp@bitbucket.org/smashml/slacx.git"
     data-push-url="https://lensonp@bitbucket.org/smashml/slacx.git"
     
     
     
     >
  <div class="aui-buttons">
    
    <button class="aui-button aui-dropdown2-trigger protocol-trigger"
            data-command-prefix="git clone"
            data-primary-https="https://lensonp@bitbucket.org/smashml/slacx.git"
            data-primary-ssh="git@bitbucket.org:smashml/slacx.git"
            aria-controls="protocols-list-header">
      <span class="dropdown-text">HTTPS</span>
    </button>
    <aui-dropdown-menu id="protocols-list-header" data-aui-alignment="bottom left">
      <aui-section id="protocols-list-section" class="aui-list-truncate">
        <aui-item-radio class="item-link https" checked>HTTPS</aui-item-radio>
        <aui-item-radio class="item-link ssh">SSH</aui-item-radio>
      </aui-section>
    </aui-dropdown-menu>
    <input type="text" readonly="readonly" class="clone-url-input"
           value="git clone https://lensonp@bitbucket.org/smashml/slacx.git">
  </div>
  
</div>

  <div class="learn-more">
    <p>Need help cloning? Learn how to
         <a href="https://confluence.atlassian.com/x/4whODQ" target="_blank">clone a repository</a>.
    </p>
  </div>
  
  <div class="sourcetree-callout clone-in-sourcetree"
  data-module="components/clone/clone-in-sourcetree"
  data-https-url="https://lensonp@bitbucket.org/smashml/slacx.git"
  data-ssh-url="ssh://git@bitbucket.org/smashml/slacx.git">

  <div>
    <button class="aui-button aui-button-primary">
      
        Clone in SourceTree
      
    </button>
  </div>

  <p class="windows-text">
    
      <a href="http://www.sourcetreeapp.com/?utm_source=internal&amp;utm_medium=link&amp;utm_campaign=clone_repo_win" target="_blank">Atlassian SourceTree</a>
      is a free Git and Mercurial client for Windows.
    
  </p>
  <p class="mac-text">
    
      <a href="http://www.sourcetreeapp.com/?utm_source=internal&amp;utm_medium=link&amp;utm_campaign=clone_repo_mac" target="_blank">Atlassian SourceTree</a>
      is a free Git and Mercurial client for Mac.
    
  </p>
</div>
</div>
</div>
  

        
  <div class="aui-page-panel ">
    
  
  
    <div class="aui-page-panel-inner">
      <div id="repo-content" class="aui-page-panel-content"
          data-module="repo/index"
          
            data-project-id="1377996"
          
          >
        
          
            <ol class="aui-nav aui-nav-breadcrumbs">
              <li>
  <a href="/smashml/">smashml</a>
</li>

  <li class="aui-nav-selected">
    <a href="/account/user/smashml/projects/SMAS">smash-xray</a>
  </li>

<li>
  <a href="/smashml/slacx">slacx</a>
</li>
              
            </ol>
          
          <div class="aui-group repo-page-header">
            <div class="aui-item section-title">
              <h1>Source</h1>
            </div>
            <div class="aui-item page-actions">
              
            </div>
          </div>
        
        
  <div id="source-container" class="maskable" data-module="repo/source/index">
    



<header id="source-path">
  
    <div class="labels labels-csv">
      <div class="aui-buttons">
        <button data-branches-tags-url="/api/1.0/repositories/smashml/slacx/branches-tags"
                data-module="components/branch-dialog"
                class="aui-button branch-dialog-trigger" title="master">
          
            
              <span class="aui-icon aui-icon-small aui-iconfont-devtools-branch">Branch</span>
            
            <span class="name">master</span>
          
          <span class="aui-icon-dropdown"></span>
        </button>
        <button class="aui-button" id="checkout-branch-button"
                title="Check out this branch">
          <span class="aui-icon aui-icon-small aui-iconfont-devtools-clone">Check out branch</span>
          <span class="aui-icon-dropdown"></span>
        </button>
      </div>
      
    <script id="branch-checkout-template" type="text/html">
      

<div id="checkout-branch-contents">
  <div class="command-line">
    <p>
      Check out this branch on your local machine to begin working on it.
    </p>
    <input type="text" class="checkout-command" readonly="readonly"
        
           value="git fetch && git checkout [[branchName]]"
        
        >
  </div>
  
    <div class="sourcetree-callout clone-in-sourcetree"
  data-module="components/clone/clone-in-sourcetree"
  data-https-url="https://lensonp@bitbucket.org/smashml/slacx.git"
  data-ssh-url="ssh://git@bitbucket.org/smashml/slacx.git">

  <div>
    <button class="aui-button aui-button-primary">
      
        Check out in SourceTree
      
    </button>
  </div>

  <p class="windows-text">
    
      <a href="http://www.sourcetreeapp.com/?utm_source=internal&amp;utm_medium=link&amp;utm_campaign=clone_repo_win" target="_blank">Atlassian SourceTree</a>
      is a free Git and Mercurial client for Windows.
    
  </p>
  <p class="mac-text">
    
      <a href="http://www.sourcetreeapp.com/?utm_source=internal&amp;utm_medium=link&amp;utm_campaign=clone_repo_mac" target="_blank">Atlassian SourceTree</a>
      is a free Git and Mercurial client for Mac.
    
  </p>
</div>
  
</div>

    </script>
  
    </div>
  
  
    <div class="secondary-actions">
      <div class="aui-buttons">
        
          <a href="/smashml/slacx/src/5b763e8d612c/core/workflow/slacxwfman.py?at=master"
            class="aui-button pjax-trigger" aria-pressed="true">
            Source
          </a>
          <a href="/smashml/slacx/diff/core/workflow/slacxwfman.py?diff2=5b763e8d612c&at=master"
            class="aui-button pjax-trigger"
            title="Diff to previous change">
            Diff
          </a>
          <a href="/smashml/slacx/history-node/5b763e8d612c/core/workflow/slacxwfman.py?at=master"
            class="aui-button pjax-trigger">
            History
          </a>
        
      </div>
    </div>
  
  <h1>
    
      
        <a href="/smashml/slacx/src/5b763e8d612c?at=master"
          class="pjax-trigger root" title="smashml/slacx at 5b763e8d612c">slacx</a> /
      
      
        
          
            <a href="/smashml/slacx/src/5b763e8d612c/core/?at=master"
              class="pjax-trigger directory-name">core</a> /
          
        
      
        
          
            <a href="/smashml/slacx/src/5b763e8d612c/core/workflow/?at=master"
              class="pjax-trigger directory-name">workflow</a> /
          
        
      
        
          
            <span class="file-name">slacxwfman.py</span>
          
        
      
    
  </h1>
  
    
    
  
  <div class="clearfix"></div>
</header>


  
    
  

  <div id="editor-container" class="maskable"
       data-module="repo/source/editor"
       data-owner="smashml"
       data-slug="slacx"
       data-is-writer="true"
       data-has-push-access="true"
       data-hash="5b763e8d612ceca1e84b0ef52fd4cc673fd4e82a"
       data-branch="master"
       data-path="core/workflow/slacxwfman.py"
       data-source-url="/api/internal/repositories/smashml/slacx/src/5b763e8d612ceca1e84b0ef52fd4cc673fd4e82a/core/workflow/slacxwfman.py">
    <div id="source-view" class="file-source-container" data-module="repo/source/view-file" data-is-lfs="false">
      <div class="toolbar">
        <div class="primary">
          <div class="aui-buttons">
            
              <button id="file-history-trigger" class="aui-button aui-button-light changeset-info"
                      data-changeset="5b763e8d612ceca1e84b0ef52fd4cc673fd4e82a"
                      data-path="core/workflow/slacxwfman.py"
                      data-current="5b763e8d612ceca1e84b0ef52fd4cc673fd4e82a">
                 

  <div class="aui-avatar aui-avatar-xsmall">
    <div class="aui-avatar-inner">
      <img src="https://bitbucket.org/account/lensonp/avatar/16/?ts=1476219911">
    </div>
  </div>
  <span class="changeset-hash">5b763e8</span>
  <time datetime="2016-10-10T18:03:20+00:00" class="timestamp"></time>
  <span class="aui-icon-dropdown"></span>

              </button>
            
          </div>
          
          <a href="/smashml/slacx/full-commit/5b763e8d612c/core/workflow/slacxwfman.py" id="full-commit-link"
             title="View full commit 5b763e8">Full commit</a>
        </div>
        <div class="secondary">
          
          <div class="aui-buttons">
            
              <a href="/smashml/slacx/annotate/5b763e8d612ceca1e84b0ef52fd4cc673fd4e82a/core/workflow/slacxwfman.py?at=master"
                 class="aui-button aui-button-light pjax-trigger">Blame</a>
              
            
            <a href="/smashml/slacx/raw/5b763e8d612ceca1e84b0ef52fd4cc673fd4e82a/core/workflow/slacxwfman.py" class="aui-button aui-button-light">Raw</a>
          </div>
          
            <div class="aui-buttons">
              
              <button id="file-edit-button" class="edit-button aui-button aui-button-light aui-button-split-main"
                  >
                Edit
                
              </button>
              <button id="file-more-actions-button" class="aui-button aui-button-light aui-dropdown2-trigger aui-button-split-more" aria-owns="split-container-dropdown" aria-haspopup="true"
                  >
                More file actions
              </button>
            </div>
            <div id="split-container-dropdown" class="aui-dropdown2 aui-style-default" data-container="#editor-container">
              <ul class="aui-list-truncate">
                <li><a href="#" data-module="repo/source/rename-file" class="rename-link">Rename</a></li>
                <li><a href="#" data-module="repo/source/delete-file" class="delete-link">Delete</a></li>
              </ul>
            </div>
          
        </div>

        <div id="fileview-dropdown"
            class="aui-dropdown2 aui-style-default"
            data-fileview-container="#fileview-container"
            
            
            data-fileview-button="#fileview-trigger"
            data-module="connect/fileview">
          <div class="aui-dropdown2-section">
            <ul>
              <li>
                <a class="aui-dropdown2-radio aui-dropdown2-checked"
                    data-fileview-id="-1"
                    data-fileview-loaded="true"
                    data-fileview-target="#fileview-original"
                    data-fileview-connection-key=""
                    data-fileview-module-key="file-view-default">
                  Default File Viewer
                </a>
              </li>
              
            </ul>
          </div>
        </div>

        <div class="clearfix"></div>
      </div>
      <div id="fileview-container">
        <div id="fileview-original"
            class="fileview"
            data-module="repo/source/highlight-lines"
            data-fileview-loaded="true">
          


  
    <div class="file-source">
      <table class="codehilite highlighttable"><tr><td class="linenos"><div class="linenodiv"><pre><a href="#slacxwfman.py-1">  1</a>
<a href="#slacxwfman.py-2">  2</a>
<a href="#slacxwfman.py-3">  3</a>
<a href="#slacxwfman.py-4">  4</a>
<a href="#slacxwfman.py-5">  5</a>
<a href="#slacxwfman.py-6">  6</a>
<a href="#slacxwfman.py-7">  7</a>
<a href="#slacxwfman.py-8">  8</a>
<a href="#slacxwfman.py-9">  9</a>
<a href="#slacxwfman.py-10"> 10</a>
<a href="#slacxwfman.py-11"> 11</a>
<a href="#slacxwfman.py-12"> 12</a>
<a href="#slacxwfman.py-13"> 13</a>
<a href="#slacxwfman.py-14"> 14</a>
<a href="#slacxwfman.py-15"> 15</a>
<a href="#slacxwfman.py-16"> 16</a>
<a href="#slacxwfman.py-17"> 17</a>
<a href="#slacxwfman.py-18"> 18</a>
<a href="#slacxwfman.py-19"> 19</a>
<a href="#slacxwfman.py-20"> 20</a>
<a href="#slacxwfman.py-21"> 21</a>
<a href="#slacxwfman.py-22"> 22</a>
<a href="#slacxwfman.py-23"> 23</a>
<a href="#slacxwfman.py-24"> 24</a>
<a href="#slacxwfman.py-25"> 25</a>
<a href="#slacxwfman.py-26"> 26</a>
<a href="#slacxwfman.py-27"> 27</a>
<a href="#slacxwfman.py-28"> 28</a>
<a href="#slacxwfman.py-29"> 29</a>
<a href="#slacxwfman.py-30"> 30</a>
<a href="#slacxwfman.py-31"> 31</a>
<a href="#slacxwfman.py-32"> 32</a>
<a href="#slacxwfman.py-33"> 33</a>
<a href="#slacxwfman.py-34"> 34</a>
<a href="#slacxwfman.py-35"> 35</a>
<a href="#slacxwfman.py-36"> 36</a>
<a href="#slacxwfman.py-37"> 37</a>
<a href="#slacxwfman.py-38"> 38</a>
<a href="#slacxwfman.py-39"> 39</a>
<a href="#slacxwfman.py-40"> 40</a>
<a href="#slacxwfman.py-41"> 41</a>
<a href="#slacxwfman.py-42"> 42</a>
<a href="#slacxwfman.py-43"> 43</a>
<a href="#slacxwfman.py-44"> 44</a>
<a href="#slacxwfman.py-45"> 45</a>
<a href="#slacxwfman.py-46"> 46</a>
<a href="#slacxwfman.py-47"> 47</a>
<a href="#slacxwfman.py-48"> 48</a>
<a href="#slacxwfman.py-49"> 49</a>
<a href="#slacxwfman.py-50"> 50</a>
<a href="#slacxwfman.py-51"> 51</a>
<a href="#slacxwfman.py-52"> 52</a>
<a href="#slacxwfman.py-53"> 53</a>
<a href="#slacxwfman.py-54"> 54</a>
<a href="#slacxwfman.py-55"> 55</a>
<a href="#slacxwfman.py-56"> 56</a>
<a href="#slacxwfman.py-57"> 57</a>
<a href="#slacxwfman.py-58"> 58</a>
<a href="#slacxwfman.py-59"> 59</a>
<a href="#slacxwfman.py-60"> 60</a>
<a href="#slacxwfman.py-61"> 61</a>
<a href="#slacxwfman.py-62"> 62</a>
<a href="#slacxwfman.py-63"> 63</a>
<a href="#slacxwfman.py-64"> 64</a>
<a href="#slacxwfman.py-65"> 65</a>
<a href="#slacxwfman.py-66"> 66</a>
<a href="#slacxwfman.py-67"> 67</a>
<a href="#slacxwfman.py-68"> 68</a>
<a href="#slacxwfman.py-69"> 69</a>
<a href="#slacxwfman.py-70"> 70</a>
<a href="#slacxwfman.py-71"> 71</a>
<a href="#slacxwfman.py-72"> 72</a>
<a href="#slacxwfman.py-73"> 73</a>
<a href="#slacxwfman.py-74"> 74</a>
<a href="#slacxwfman.py-75"> 75</a>
<a href="#slacxwfman.py-76"> 76</a>
<a href="#slacxwfman.py-77"> 77</a>
<a href="#slacxwfman.py-78"> 78</a>
<a href="#slacxwfman.py-79"> 79</a>
<a href="#slacxwfman.py-80"> 80</a>
<a href="#slacxwfman.py-81"> 81</a>
<a href="#slacxwfman.py-82"> 82</a>
<a href="#slacxwfman.py-83"> 83</a>
<a href="#slacxwfman.py-84"> 84</a>
<a href="#slacxwfman.py-85"> 85</a>
<a href="#slacxwfman.py-86"> 86</a>
<a href="#slacxwfman.py-87"> 87</a>
<a href="#slacxwfman.py-88"> 88</a>
<a href="#slacxwfman.py-89"> 89</a>
<a href="#slacxwfman.py-90"> 90</a>
<a href="#slacxwfman.py-91"> 91</a>
<a href="#slacxwfman.py-92"> 92</a>
<a href="#slacxwfman.py-93"> 93</a>
<a href="#slacxwfman.py-94"> 94</a>
<a href="#slacxwfman.py-95"> 95</a>
<a href="#slacxwfman.py-96"> 96</a>
<a href="#slacxwfman.py-97"> 97</a>
<a href="#slacxwfman.py-98"> 98</a>
<a href="#slacxwfman.py-99"> 99</a>
<a href="#slacxwfman.py-100">100</a>
<a href="#slacxwfman.py-101">101</a>
<a href="#slacxwfman.py-102">102</a>
<a href="#slacxwfman.py-103">103</a>
<a href="#slacxwfman.py-104">104</a>
<a href="#slacxwfman.py-105">105</a>
<a href="#slacxwfman.py-106">106</a>
<a href="#slacxwfman.py-107">107</a>
<a href="#slacxwfman.py-108">108</a>
<a href="#slacxwfman.py-109">109</a>
<a href="#slacxwfman.py-110">110</a>
<a href="#slacxwfman.py-111">111</a>
<a href="#slacxwfman.py-112">112</a>
<a href="#slacxwfman.py-113">113</a>
<a href="#slacxwfman.py-114">114</a>
<a href="#slacxwfman.py-115">115</a>
<a href="#slacxwfman.py-116">116</a>
<a href="#slacxwfman.py-117">117</a>
<a href="#slacxwfman.py-118">118</a>
<a href="#slacxwfman.py-119">119</a>
<a href="#slacxwfman.py-120">120</a>
<a href="#slacxwfman.py-121">121</a>
<a href="#slacxwfman.py-122">122</a>
<a href="#slacxwfman.py-123">123</a>
<a href="#slacxwfman.py-124">124</a>
<a href="#slacxwfman.py-125">125</a>
<a href="#slacxwfman.py-126">126</a>
<a href="#slacxwfman.py-127">127</a>
<a href="#slacxwfman.py-128">128</a>
<a href="#slacxwfman.py-129">129</a>
<a href="#slacxwfman.py-130">130</a>
<a href="#slacxwfman.py-131">131</a>
<a href="#slacxwfman.py-132">132</a>
<a href="#slacxwfman.py-133">133</a>
<a href="#slacxwfman.py-134">134</a>
<a href="#slacxwfman.py-135">135</a>
<a href="#slacxwfman.py-136">136</a>
<a href="#slacxwfman.py-137">137</a>
<a href="#slacxwfman.py-138">138</a>
<a href="#slacxwfman.py-139">139</a>
<a href="#slacxwfman.py-140">140</a>
<a href="#slacxwfman.py-141">141</a>
<a href="#slacxwfman.py-142">142</a>
<a href="#slacxwfman.py-143">143</a>
<a href="#slacxwfman.py-144">144</a>
<a href="#slacxwfman.py-145">145</a>
<a href="#slacxwfman.py-146">146</a>
<a href="#slacxwfman.py-147">147</a>
<a href="#slacxwfman.py-148">148</a>
<a href="#slacxwfman.py-149">149</a>
<a href="#slacxwfman.py-150">150</a>
<a href="#slacxwfman.py-151">151</a>
<a href="#slacxwfman.py-152">152</a>
<a href="#slacxwfman.py-153">153</a>
<a href="#slacxwfman.py-154">154</a>
<a href="#slacxwfman.py-155">155</a>
<a href="#slacxwfman.py-156">156</a>
<a href="#slacxwfman.py-157">157</a>
<a href="#slacxwfman.py-158">158</a>
<a href="#slacxwfman.py-159">159</a>
<a href="#slacxwfman.py-160">160</a>
<a href="#slacxwfman.py-161">161</a>
<a href="#slacxwfman.py-162">162</a>
<a href="#slacxwfman.py-163">163</a>
<a href="#slacxwfman.py-164">164</a>
<a href="#slacxwfman.py-165">165</a>
<a href="#slacxwfman.py-166">166</a>
<a href="#slacxwfman.py-167">167</a>
<a href="#slacxwfman.py-168">168</a>
<a href="#slacxwfman.py-169">169</a>
<a href="#slacxwfman.py-170">170</a>
<a href="#slacxwfman.py-171">171</a>
<a href="#slacxwfman.py-172">172</a>
<a href="#slacxwfman.py-173">173</a>
<a href="#slacxwfman.py-174">174</a>
<a href="#slacxwfman.py-175">175</a>
<a href="#slacxwfman.py-176">176</a>
<a href="#slacxwfman.py-177">177</a>
<a href="#slacxwfman.py-178">178</a>
<a href="#slacxwfman.py-179">179</a>
<a href="#slacxwfman.py-180">180</a>
<a href="#slacxwfman.py-181">181</a>
<a href="#slacxwfman.py-182">182</a>
<a href="#slacxwfman.py-183">183</a>
<a href="#slacxwfman.py-184">184</a>
<a href="#slacxwfman.py-185">185</a>
<a href="#slacxwfman.py-186">186</a>
<a href="#slacxwfman.py-187">187</a>
<a href="#slacxwfman.py-188">188</a>
<a href="#slacxwfman.py-189">189</a>
<a href="#slacxwfman.py-190">190</a>
<a href="#slacxwfman.py-191">191</a>
<a href="#slacxwfman.py-192">192</a>
<a href="#slacxwfman.py-193">193</a>
<a href="#slacxwfman.py-194">194</a>
<a href="#slacxwfman.py-195">195</a>
<a href="#slacxwfman.py-196">196</a>
<a href="#slacxwfman.py-197">197</a>
<a href="#slacxwfman.py-198">198</a>
<a href="#slacxwfman.py-199">199</a>
<a href="#slacxwfman.py-200">200</a>
<a href="#slacxwfman.py-201">201</a>
<a href="#slacxwfman.py-202">202</a>
<a href="#slacxwfman.py-203">203</a>
<a href="#slacxwfman.py-204">204</a>
<a href="#slacxwfman.py-205">205</a>
<a href="#slacxwfman.py-206">206</a>
<a href="#slacxwfman.py-207">207</a>
<a href="#slacxwfman.py-208">208</a>
<a href="#slacxwfman.py-209">209</a>
<a href="#slacxwfman.py-210">210</a>
<a href="#slacxwfman.py-211">211</a>
<a href="#slacxwfman.py-212">212</a>
<a href="#slacxwfman.py-213">213</a>
<a href="#slacxwfman.py-214">214</a>
<a href="#slacxwfman.py-215">215</a>
<a href="#slacxwfman.py-216">216</a>
<a href="#slacxwfman.py-217">217</a>
<a href="#slacxwfman.py-218">218</a>
<a href="#slacxwfman.py-219">219</a>
<a href="#slacxwfman.py-220">220</a>
<a href="#slacxwfman.py-221">221</a>
<a href="#slacxwfman.py-222">222</a>
<a href="#slacxwfman.py-223">223</a>
<a href="#slacxwfman.py-224">224</a>
<a href="#slacxwfman.py-225">225</a>
<a href="#slacxwfman.py-226">226</a>
<a href="#slacxwfman.py-227">227</a>
<a href="#slacxwfman.py-228">228</a>
<a href="#slacxwfman.py-229">229</a>
<a href="#slacxwfman.py-230">230</a>
<a href="#slacxwfman.py-231">231</a>
<a href="#slacxwfman.py-232">232</a>
<a href="#slacxwfman.py-233">233</a>
<a href="#slacxwfman.py-234">234</a>
<a href="#slacxwfman.py-235">235</a>
<a href="#slacxwfman.py-236">236</a>
<a href="#slacxwfman.py-237">237</a>
<a href="#slacxwfman.py-238">238</a>
<a href="#slacxwfman.py-239">239</a>
<a href="#slacxwfman.py-240">240</a>
<a href="#slacxwfman.py-241">241</a>
<a href="#slacxwfman.py-242">242</a>
<a href="#slacxwfman.py-243">243</a>
<a href="#slacxwfman.py-244">244</a>
<a href="#slacxwfman.py-245">245</a>
<a href="#slacxwfman.py-246">246</a>
<a href="#slacxwfman.py-247">247</a>
<a href="#slacxwfman.py-248">248</a>
<a href="#slacxwfman.py-249">249</a>
<a href="#slacxwfman.py-250">250</a>
<a href="#slacxwfman.py-251">251</a>
<a href="#slacxwfman.py-252">252</a>
<a href="#slacxwfman.py-253">253</a>
<a href="#slacxwfman.py-254">254</a>
<a href="#slacxwfman.py-255">255</a>
<a href="#slacxwfman.py-256">256</a>
<a href="#slacxwfman.py-257">257</a>
<a href="#slacxwfman.py-258">258</a>
<a href="#slacxwfman.py-259">259</a>
<a href="#slacxwfman.py-260">260</a>
<a href="#slacxwfman.py-261">261</a>
<a href="#slacxwfman.py-262">262</a>
<a href="#slacxwfman.py-263">263</a>
<a href="#slacxwfman.py-264">264</a>
<a href="#slacxwfman.py-265">265</a></pre></div></td><td class="code"><div class="codehilite highlight"><pre><span></span><a name="slacxwfman.py-1"></a><span class="kn">from</span> <span class="nn">PySide</span> <span class="kn">import</span> <span class="n">QtCore</span>
<a name="slacxwfman.py-2"></a>
<a name="slacxwfman.py-3"></a><span class="kn">from</span> <span class="nn">..treemodel</span> <span class="kn">import</span> <span class="n">TreeModel</span>
<a name="slacxwfman.py-4"></a><span class="kn">from</span> <span class="nn">..treeitem</span> <span class="kn">import</span> <span class="n">TreeItem</span>
<a name="slacxwfman.py-5"></a><span class="kn">from</span> <span class="nn">..operations</span> <span class="kn">import</span> <span class="n">optools</span>
<a name="slacxwfman.py-6"></a>
<a name="slacxwfman.py-7"></a><span class="c1"># TODO: See note on remove_op()</span>
<a name="slacxwfman.py-8"></a>
<a name="slacxwfman.py-9"></a><span class="k">class</span> <span class="nc">WfManager</span><span class="p">(</span><span class="n">TreeModel</span><span class="p">):</span>
<a name="slacxwfman.py-10"></a>    <span class="sd">&quot;&quot;&quot;</span>
<a name="slacxwfman.py-11"></a><span class="sd">    Class for managing a workflow built from slacx operations.</span>
<a name="slacxwfman.py-12"></a><span class="sd">    &quot;&quot;&quot;</span>
<a name="slacxwfman.py-13"></a>
<a name="slacxwfman.py-14"></a>    <span class="k">def</span> <span class="nf">__init__</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class="o">**</span><span class="n">kwargs</span><span class="p">):</span>
<a name="slacxwfman.py-15"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">_n_loaded</span> <span class="o">=</span> <span class="mi">0</span> 
<a name="slacxwfman.py-16"></a>        <span class="c1">#TODO: build a saved tree from kwargs</span>
<a name="slacxwfman.py-17"></a>        <span class="c1">#if &#39;wf_loader&#39; in kwargs:</span>
<a name="slacxwfman.py-18"></a>        <span class="c1">#    with f as open(wf_loader,&#39;r&#39;): </span>
<a name="slacxwfman.py-19"></a>        <span class="c1">#        self.load_from_file(f)</span>
<a name="slacxwfman.py-20"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">_wf_dict</span> <span class="o">=</span> <span class="p">{}</span>       <span class="c1"># this will be a dict for a dask.threaded graph </span>
<a name="slacxwfman.py-21"></a>        <span class="k">if</span> <span class="s1">&#39;imgman&#39;</span> <span class="ow">in</span> <span class="n">kwargs</span><span class="p">:</span>
<a name="slacxwfman.py-22"></a>            <span class="bp">self</span><span class="o">.</span><span class="n">imgman</span> <span class="o">=</span> <span class="n">kwargs</span><span class="p">[</span><span class="s1">&#39;imgman&#39;</span><span class="p">]</span> 
<a name="slacxwfman.py-23"></a>        <span class="nb">super</span><span class="p">(</span><span class="n">WfManager</span><span class="p">,</span><span class="bp">self</span><span class="p">)</span><span class="o">.</span><span class="n">__init__</span><span class="p">()</span>
<a name="slacxwfman.py-24"></a>
<a name="slacxwfman.py-25"></a>    <span class="k">def</span> <span class="nf">add_op</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class="n">new_op</span><span class="p">,</span><span class="n">tag</span><span class="p">):</span>
<a name="slacxwfman.py-26"></a>        <span class="sd">&quot;&quot;&quot;Add an Operation to the tree as a new top-level TreeItem.&quot;&quot;&quot;</span>
<a name="slacxwfman.py-27"></a>        <span class="c1"># Count top-level rows by passing parent=QModelIndex()</span>
<a name="slacxwfman.py-28"></a>        <span class="n">ins_row</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">rowCount</span><span class="p">(</span><span class="n">QtCore</span><span class="o">.</span><span class="n">QModelIndex</span><span class="p">())</span>
<a name="slacxwfman.py-29"></a>        <span class="c1"># Make a new TreeItem, column 0, invalid parent </span>
<a name="slacxwfman.py-30"></a>        <span class="n">new_treeitem</span> <span class="o">=</span> <span class="n">TreeItem</span><span class="p">(</span><span class="n">ins_row</span><span class="p">,</span><span class="mi">0</span><span class="p">,</span><span class="n">QtCore</span><span class="o">.</span><span class="n">QModelIndex</span><span class="p">())</span>
<a name="slacxwfman.py-31"></a>        <span class="n">new_treeitem</span><span class="o">.</span><span class="n">data</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">new_op</span><span class="p">)</span>
<a name="slacxwfman.py-32"></a>        <span class="n">new_treeitem</span><span class="o">.</span><span class="n">set_tag</span><span class="p">(</span> <span class="n">tag</span> <span class="p">)</span>
<a name="slacxwfman.py-33"></a>        <span class="n">new_treeitem</span><span class="o">.</span><span class="n">long_tag</span> <span class="o">=</span> <span class="n">new_op</span><span class="o">.</span><span class="n">__doc__</span>
<a name="slacxwfman.py-34"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">beginInsertRows</span><span class="p">(</span>
<a name="slacxwfman.py-35"></a>        <span class="n">QtCore</span><span class="o">.</span><span class="n">QModelIndex</span><span class="p">(),</span><span class="n">ins_row</span><span class="p">,</span><span class="n">ins_row</span><span class="p">)</span>
<a name="slacxwfman.py-36"></a>        <span class="c1"># Insertion occurs between notification methods</span>
<a name="slacxwfman.py-37"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">root_items</span><span class="o">.</span><span class="n">insert</span><span class="p">(</span><span class="n">ins_row</span><span class="p">,</span><span class="n">new_treeitem</span><span class="p">)</span>
<a name="slacxwfman.py-38"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">endInsertRows</span><span class="p">()</span>
<a name="slacxwfman.py-39"></a>        <span class="c1"># Render Operation inputs and outputs as children</span>
<a name="slacxwfman.py-40"></a>        <span class="n">indx</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">index</span><span class="p">(</span><span class="n">ins_row</span><span class="p">,</span><span class="mi">0</span><span class="p">,</span><span class="n">QtCore</span><span class="o">.</span><span class="n">QModelIndex</span><span class="p">())</span>
<a name="slacxwfman.py-41"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">io_subtree</span><span class="p">(</span><span class="n">new_op</span><span class="p">,</span><span class="n">indx</span><span class="p">)</span>
<a name="slacxwfman.py-42"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">_n_loaded</span> <span class="o">+=</span> <span class="mi">1</span>
<a name="slacxwfman.py-43"></a>
<a name="slacxwfman.py-44"></a>    <span class="k">def</span> <span class="nf">update_op</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class="n">indx</span><span class="p">,</span><span class="n">new_op</span><span class="p">):</span>
<a name="slacxwfman.py-45"></a>        <span class="sd">&quot;&quot;&quot;Replace Operation at indx with new_op&quot;&quot;&quot;</span>
<a name="slacxwfman.py-46"></a>        <span class="c1"># Get the treeitem for indx</span>
<a name="slacxwfman.py-47"></a>        <span class="n">item</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">get_item</span><span class="p">(</span><span class="n">indx</span><span class="p">)</span>
<a name="slacxwfman.py-48"></a>        <span class="c1"># Put the data in the treeitem</span>
<a name="slacxwfman.py-49"></a>        <span class="n">item</span><span class="o">.</span><span class="n">data</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span> <span class="o">=</span> <span class="n">new_op</span>
<a name="slacxwfman.py-50"></a>        <span class="n">item</span><span class="o">.</span><span class="n">long_tag</span> <span class="o">=</span> <span class="n">new_op</span><span class="o">.</span><span class="n">__doc__</span>
<a name="slacxwfman.py-51"></a>        <span class="c1"># Wipe out the children</span>
<a name="slacxwfman.py-52"></a>        <span class="c1">#for child in item.children:</span>
<a name="slacxwfman.py-53"></a>        <span class="c1">#    del child</span>
<a name="slacxwfman.py-54"></a>        <span class="c1"># Update the op subtree</span>
<a name="slacxwfman.py-55"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">build_io_subtrees</span><span class="p">(</span><span class="n">new_op</span><span class="p">,</span><span class="n">indx</span><span class="p">)</span>
<a name="slacxwfman.py-56"></a>        <span class="c1"># TODO: update gui arg frames</span>
<a name="slacxwfman.py-57"></a>
<a name="slacxwfman.py-58"></a>    <span class="k">def</span> <span class="nf">io_subtree</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class="n">op</span><span class="p">,</span><span class="n">parent</span><span class="p">):</span>
<a name="slacxwfman.py-59"></a>        <span class="sd">&quot;&quot;&quot;Add inputs and outputs subtrees as children of an Operation TreeItem&quot;&quot;&quot;</span>
<a name="slacxwfman.py-60"></a>        <span class="c1"># Get a reference to the parent item</span>
<a name="slacxwfman.py-61"></a>        <span class="n">p_item</span> <span class="o">=</span> <span class="n">parent</span><span class="o">.</span><span class="n">internalPointer</span><span class="p">()</span>
<a name="slacxwfman.py-62"></a>        <span class="c1"># TreeItems as placeholders for inputs, outputs lists</span>
<a name="slacxwfman.py-63"></a>        <span class="n">inputs_treeitem</span> <span class="o">=</span> <span class="n">TreeItem</span><span class="p">(</span><span class="mi">0</span><span class="p">,</span><span class="mi">0</span><span class="p">,</span><span class="n">parent</span><span class="p">)</span>
<a name="slacxwfman.py-64"></a>        <span class="n">inputs_treeitem</span><span class="o">.</span><span class="n">set_tag</span><span class="p">(</span><span class="s1">&#39;Inputs&#39;</span><span class="p">)</span>
<a name="slacxwfman.py-65"></a>        <span class="n">outputs_treeitem</span> <span class="o">=</span> <span class="n">TreeItem</span><span class="p">(</span><span class="mi">1</span><span class="p">,</span><span class="mi">0</span><span class="p">,</span><span class="n">parent</span><span class="p">)</span>
<a name="slacxwfman.py-66"></a>        <span class="n">outputs_treeitem</span><span class="o">.</span><span class="n">set_tag</span><span class="p">(</span><span class="s1">&#39;Outputs&#39;</span><span class="p">)</span>
<a name="slacxwfman.py-67"></a>        <span class="c1"># Insert the new TreeItems</span>
<a name="slacxwfman.py-68"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">beginInsertRows</span><span class="p">(</span><span class="n">parent</span><span class="p">,</span><span class="mi">0</span><span class="p">,</span><span class="mi">1</span><span class="p">)</span>
<a name="slacxwfman.py-69"></a>        <span class="n">p_item</span><span class="o">.</span><span class="n">children</span><span class="o">.</span><span class="n">insert</span><span class="p">(</span><span class="mi">0</span><span class="p">,</span><span class="n">inputs_treeitem</span><span class="p">)</span>
<a name="slacxwfman.py-70"></a>        <span class="n">p_item</span><span class="o">.</span><span class="n">children</span><span class="o">.</span><span class="n">insert</span><span class="p">(</span><span class="mi">1</span><span class="p">,</span><span class="n">outputs_treeitem</span><span class="p">)</span>
<a name="slacxwfman.py-71"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">endInsertRows</span><span class="p">()</span>
<a name="slacxwfman.py-72"></a>        <span class="c1"># Populate the new TreeItems with op.inputs and op.outputs</span>
<a name="slacxwfman.py-73"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">build_io_subtrees</span><span class="p">(</span><span class="n">op</span><span class="p">,</span><span class="n">parent</span><span class="p">)</span>
<a name="slacxwfman.py-74"></a>
<a name="slacxwfman.py-75"></a>    <span class="k">def</span> <span class="nf">build_io_subtrees</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class="n">op</span><span class="p">,</span><span class="n">parent</span><span class="p">):</span>
<a name="slacxwfman.py-76"></a>        <span class="c1"># Get a reference to the parent item</span>
<a name="slacxwfman.py-77"></a>        <span class="n">p_item</span> <span class="o">=</span> <span class="n">parent</span><span class="o">.</span><span class="n">internalPointer</span><span class="p">()</span>
<a name="slacxwfman.py-78"></a>        <span class="c1"># Get references to the inputs and outputs subtrees</span>
<a name="slacxwfman.py-79"></a>        <span class="n">inputs_treeitem</span> <span class="o">=</span> <span class="n">p_item</span><span class="o">.</span><span class="n">children</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span>
<a name="slacxwfman.py-80"></a>        <span class="n">outputs_treeitem</span> <span class="o">=</span> <span class="n">p_item</span><span class="o">.</span><span class="n">children</span><span class="p">[</span><span class="mi">1</span><span class="p">]</span>
<a name="slacxwfman.py-81"></a>        <span class="c1"># Get the QModelIndexes of the subtrees </span>
<a name="slacxwfman.py-82"></a>        <span class="n">inputs_indx</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">index</span><span class="p">(</span><span class="mi">0</span><span class="p">,</span><span class="mi">0</span><span class="p">,</span><span class="n">parent</span><span class="p">)</span>
<a name="slacxwfman.py-83"></a>        <span class="n">outputs_indx</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">index</span><span class="p">(</span><span class="mi">1</span><span class="p">,</span><span class="mi">0</span><span class="p">,</span><span class="n">parent</span><span class="p">)</span>
<a name="slacxwfman.py-84"></a>        <span class="c1"># Eliminate their children</span>
<a name="slacxwfman.py-85"></a>        <span class="n">nc_i</span> <span class="o">=</span> <span class="n">inputs_treeitem</span><span class="o">.</span><span class="n">n_children</span><span class="p">()</span>
<a name="slacxwfman.py-86"></a>        <span class="n">nc_o</span> <span class="o">=</span> <span class="n">outputs_treeitem</span><span class="o">.</span><span class="n">n_children</span><span class="p">()</span>
<a name="slacxwfman.py-87"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">removeRows</span><span class="p">(</span><span class="mi">0</span><span class="p">,</span><span class="n">nc_i</span><span class="p">,</span><span class="n">inputs_indx</span><span class="p">)</span>
<a name="slacxwfman.py-88"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">removeRows</span><span class="p">(</span><span class="mi">0</span><span class="p">,</span><span class="n">nc_o</span><span class="p">,</span><span class="n">outputs_indx</span><span class="p">)</span>
<a name="slacxwfman.py-89"></a>        <span class="c1"># Populate new inputs and outputs</span>
<a name="slacxwfman.py-90"></a>        <span class="n">n_inputs</span> <span class="o">=</span> <span class="nb">len</span><span class="p">(</span><span class="n">op</span><span class="o">.</span><span class="n">inputs</span><span class="p">)</span>
<a name="slacxwfman.py-91"></a>        <span class="n">input_items</span> <span class="o">=</span> <span class="n">op</span><span class="o">.</span><span class="n">inputs</span><span class="o">.</span><span class="n">items</span><span class="p">()</span>
<a name="slacxwfman.py-92"></a>        <span class="n">n_outputs</span> <span class="o">=</span> <span class="nb">len</span><span class="p">(</span><span class="n">op</span><span class="o">.</span><span class="n">outputs</span><span class="p">)</span>
<a name="slacxwfman.py-93"></a>        <span class="n">output_items</span> <span class="o">=</span> <span class="n">op</span><span class="o">.</span><span class="n">outputs</span><span class="o">.</span><span class="n">items</span><span class="p">()</span>
<a name="slacxwfman.py-94"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">beginInsertRows</span><span class="p">(</span><span class="n">inputs_indx</span><span class="p">,</span><span class="mi">0</span><span class="p">,</span><span class="n">n_inputs</span><span class="o">-</span><span class="mi">1</span><span class="p">)</span>
<a name="slacxwfman.py-95"></a>        <span class="k">for</span> <span class="n">i</span> <span class="ow">in</span> <span class="nb">range</span><span class="p">(</span><span class="n">n_inputs</span><span class="p">):</span>
<a name="slacxwfman.py-96"></a>            <span class="n">name</span><span class="p">,</span><span class="n">val</span> <span class="o">=</span> <span class="n">input_items</span><span class="p">[</span><span class="n">i</span><span class="p">]</span>
<a name="slacxwfman.py-97"></a>            <span class="n">inp_treeitem</span> <span class="o">=</span> <span class="n">TreeItem</span><span class="p">(</span><span class="n">i</span><span class="p">,</span><span class="mi">0</span><span class="p">,</span><span class="n">inputs_indx</span><span class="p">)</span>
<a name="slacxwfman.py-98"></a>            <span class="n">inp_treeitem</span><span class="o">.</span><span class="n">set_tag</span><span class="p">(</span><span class="n">name</span><span class="p">)</span>
<a name="slacxwfman.py-99"></a>            <span class="c1"># generate long tag from optools.parameter_doc(name,val,doc)</span>
<a name="slacxwfman.py-100"></a>            <span class="n">inp_treeitem</span><span class="o">.</span><span class="n">long_tag</span> <span class="o">=</span> <span class="n">optools</span><span class="o">.</span><span class="n">parameter_doc</span><span class="p">(</span><span class="n">name</span><span class="p">,</span><span class="n">val</span><span class="p">,</span><span class="n">op</span><span class="o">.</span><span class="n">input_doc</span><span class="p">[</span><span class="n">name</span><span class="p">])</span>
<a name="slacxwfman.py-101"></a>            <span class="n">inp_treeitem</span><span class="o">.</span><span class="n">data</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">val</span><span class="p">)</span>
<a name="slacxwfman.py-102"></a>            <span class="n">inputs_treeitem</span><span class="o">.</span><span class="n">children</span><span class="o">.</span><span class="n">insert</span><span class="p">(</span><span class="n">i</span><span class="p">,</span><span class="n">inp_treeitem</span><span class="p">)</span>
<a name="slacxwfman.py-103"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">endInsertRows</span><span class="p">()</span>
<a name="slacxwfman.py-104"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">beginInsertRows</span><span class="p">(</span><span class="n">outputs_indx</span><span class="p">,</span><span class="mi">0</span><span class="p">,</span><span class="n">n_outputs</span><span class="o">-</span><span class="mi">1</span><span class="p">)</span>
<a name="slacxwfman.py-105"></a>        <span class="k">for</span> <span class="n">i</span> <span class="ow">in</span> <span class="nb">range</span><span class="p">(</span><span class="n">n_outputs</span><span class="p">):</span>
<a name="slacxwfman.py-106"></a>            <span class="n">name</span><span class="p">,</span><span class="n">val</span> <span class="o">=</span> <span class="n">output_items</span><span class="p">[</span><span class="n">i</span><span class="p">]</span>
<a name="slacxwfman.py-107"></a>            <span class="n">out_treeitem</span> <span class="o">=</span> <span class="n">TreeItem</span><span class="p">(</span><span class="n">i</span><span class="p">,</span><span class="mi">0</span><span class="p">,</span><span class="n">outputs_indx</span><span class="p">)</span>
<a name="slacxwfman.py-108"></a>            <span class="n">out_treeitem</span><span class="o">.</span><span class="n">set_tag</span><span class="p">(</span><span class="n">name</span><span class="p">)</span>
<a name="slacxwfman.py-109"></a>            <span class="n">out_treeitem</span><span class="o">.</span><span class="n">long_tag</span> <span class="o">=</span> <span class="n">optools</span><span class="o">.</span><span class="n">parameter_doc</span><span class="p">(</span><span class="n">name</span><span class="p">,</span><span class="n">val</span><span class="p">,</span><span class="n">op</span><span class="o">.</span><span class="n">output_doc</span><span class="p">[</span><span class="n">name</span><span class="p">])</span>
<a name="slacxwfman.py-110"></a>            <span class="n">out_treeitem</span><span class="o">.</span><span class="n">data</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">val</span><span class="p">)</span>
<a name="slacxwfman.py-111"></a>            <span class="n">outputs_treeitem</span><span class="o">.</span><span class="n">children</span><span class="o">.</span><span class="n">insert</span><span class="p">(</span><span class="n">i</span><span class="p">,</span><span class="n">out_treeitem</span><span class="p">)</span>
<a name="slacxwfman.py-112"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">endInsertRows</span><span class="p">()</span>
<a name="slacxwfman.py-113"></a>
<a name="slacxwfman.py-114"></a>    <span class="k">def</span> <span class="nf">remove_op</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class="n">rm_indx</span><span class="p">):</span>
<a name="slacxwfman.py-115"></a>        <span class="sd">&quot;&quot;&quot;Remove an Operation from the workflow tree&quot;&quot;&quot;</span>
<a name="slacxwfman.py-116"></a>        <span class="n">rm_row</span> <span class="o">=</span> <span class="n">rm_indx</span><span class="o">.</span><span class="n">row</span><span class="p">()</span>
<a name="slacxwfman.py-117"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">beginRemoveRows</span><span class="p">(</span>
<a name="slacxwfman.py-118"></a>        <span class="n">QtCore</span><span class="o">.</span><span class="n">QModelIndex</span><span class="p">(),</span><span class="n">rm_row</span><span class="p">,</span><span class="n">rm_row</span><span class="p">)</span>
<a name="slacxwfman.py-119"></a>        <span class="c1"># Removal occurs between notification methods</span>
<a name="slacxwfman.py-120"></a>        <span class="n">item_removed</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">root_items</span><span class="o">.</span><span class="n">pop</span><span class="p">(</span><span class="n">rm_row</span><span class="p">)</span>
<a name="slacxwfman.py-121"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">endRemoveRows</span><span class="p">()</span>
<a name="slacxwfman.py-122"></a>        <span class="c1"># TODO: update any Operations that depended on the removed one</span>
<a name="slacxwfman.py-123"></a>
<a name="slacxwfman.py-124"></a>    <span class="c1"># Overloaded headerData for WfManager </span>
<a name="slacxwfman.py-125"></a>    <span class="k">def</span> <span class="nf">headerData</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class="n">section</span><span class="p">,</span><span class="n">orientation</span><span class="p">,</span><span class="n">data_role</span><span class="p">):</span>
<a name="slacxwfman.py-126"></a>        <span class="k">if</span> <span class="p">(</span><span class="n">data_role</span> <span class="o">==</span> <span class="n">QtCore</span><span class="o">.</span><span class="n">Qt</span><span class="o">.</span><span class="n">DisplayRole</span> <span class="ow">and</span> <span class="n">section</span> <span class="o">==</span> <span class="mi">0</span><span class="p">):</span>
<a name="slacxwfman.py-127"></a>            <span class="k">return</span> <span class="s2">&quot;{} operation(s) loaded&quot;</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">rowCount</span><span class="p">(</span><span class="n">QtCore</span><span class="o">.</span><span class="n">QModelIndex</span><span class="p">()))</span>
<a name="slacxwfman.py-128"></a>        <span class="k">elif</span> <span class="p">(</span><span class="n">data_role</span> <span class="o">==</span> <span class="n">QtCore</span><span class="o">.</span><span class="n">Qt</span><span class="o">.</span><span class="n">DisplayRole</span> <span class="ow">and</span> <span class="n">section</span> <span class="o">==</span> <span class="mi">1</span><span class="p">):</span>
<a name="slacxwfman.py-129"></a>            <span class="k">return</span> <span class="s2">&quot;info&quot;</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">rowCount</span><span class="p">(</span><span class="n">QtCore</span><span class="o">.</span><span class="n">QModelIndex</span><span class="p">()))</span>
<a name="slacxwfman.py-130"></a>        <span class="k">else</span><span class="p">:</span>
<a name="slacxwfman.py-131"></a>            <span class="k">return</span> <span class="bp">None</span>
<a name="slacxwfman.py-132"></a>
<a name="slacxwfman.py-133"></a>    <span class="k">def</span> <span class="nf">check_wf</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span>
<a name="slacxwfman.py-134"></a>        <span class="sd">&quot;&quot;&quot;</span>
<a name="slacxwfman.py-135"></a><span class="sd">        Check the dependencies of the workflow.</span>
<a name="slacxwfman.py-136"></a><span class="sd">        Ensure that all loaded operations have inputs that make sense.</span>
<a name="slacxwfman.py-137"></a><span class="sd">        &quot;&quot;&quot;</span>
<a name="slacxwfman.py-138"></a>        <span class="k">pass</span>
<a name="slacxwfman.py-139"></a>
<a name="slacxwfman.py-140"></a>    <span class="k">def</span> <span class="nf">run_wf_serial</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span>
<a name="slacxwfman.py-141"></a>        <span class="sd">&quot;&quot;&quot;</span>
<a name="slacxwfman.py-142"></a><span class="sd">        Run the workflow by looping over Operations in self.root_items, </span>
<a name="slacxwfman.py-143"></a><span class="sd">        finding which ones are ready, and running them. </span>
<a name="slacxwfman.py-144"></a><span class="sd">        Repeat until no further Operations are ready.</span>
<a name="slacxwfman.py-145"></a><span class="sd">        &quot;&quot;&quot;</span>
<a name="slacxwfman.py-146"></a>        <span class="n">ops_done</span> <span class="o">=</span> <span class="p">[]</span>
<a name="slacxwfman.py-147"></a>        <span class="n">to_run</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">ops_ready</span><span class="p">(</span><span class="n">ops_done</span><span class="p">)</span>
<a name="slacxwfman.py-148"></a>        <span class="k">while</span> <span class="nb">len</span><span class="p">(</span><span class="n">to_run</span><span class="p">)</span> <span class="o">&gt;</span> <span class="mi">0</span><span class="p">:</span>
<a name="slacxwfman.py-149"></a>            <span class="k">print</span> <span class="s1">&#39;ops to run: {}&#39;</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="n">to_run</span><span class="p">)</span>
<a name="slacxwfman.py-150"></a>            <span class="k">for</span> <span class="n">j</span> <span class="ow">in</span> <span class="n">to_run</span><span class="p">:</span>
<a name="slacxwfman.py-151"></a>                <span class="n">item</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">root_items</span><span class="p">[</span><span class="n">j</span><span class="p">]</span>
<a name="slacxwfman.py-152"></a>                <span class="c1"># Get QModelIndex of this item for later use in updating tree view</span>
<a name="slacxwfman.py-153"></a>                <span class="n">indx</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">index</span><span class="p">(</span><span class="n">j</span><span class="p">,</span><span class="mi">0</span><span class="p">,</span><span class="n">QtCore</span><span class="o">.</span><span class="n">QModelIndex</span><span class="p">())</span>
<a name="slacxwfman.py-154"></a>                <span class="n">op</span> <span class="o">=</span> <span class="n">item</span><span class="o">.</span><span class="n">data</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span>
<a name="slacxwfman.py-155"></a>                <span class="c1">#print &#39;op {}: {}&#39;.format(j,type(op).__name__)</span>
<a name="slacxwfman.py-156"></a>                <span class="k">for</span> <span class="n">name</span><span class="p">,</span><span class="n">val</span> <span class="ow">in</span> <span class="n">op</span><span class="o">.</span><span class="n">inputs</span><span class="o">.</span><span class="n">items</span><span class="p">():</span>
<a name="slacxwfman.py-157"></a>                    <span class="n">op</span><span class="o">.</span><span class="n">inputs</span><span class="p">[</span><span class="n">name</span><span class="p">]</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">locate_input</span><span class="p">(</span><span class="n">val</span><span class="p">)</span>
<a name="slacxwfman.py-158"></a>                <span class="c1">#print &#39;op {} inputs: {}&#39;.format(j,op.inputs)</span>
<a name="slacxwfman.py-159"></a>                <span class="c1">#print &#39;BEFORE: op {} outputs: {}&#39;.format(j,op.outputs)</span>
<a name="slacxwfman.py-160"></a>                <span class="n">op</span><span class="o">.</span><span class="n">run</span><span class="p">()</span>
<a name="slacxwfman.py-161"></a>                <span class="c1">#print &#39;op {} called run()&#39;.format(j)</span>
<a name="slacxwfman.py-162"></a>                <span class="c1">#print &#39;AFTER: op {} outputs: {}&#39;.format(j,op.outputs)</span>
<a name="slacxwfman.py-163"></a>                <span class="n">ops_done</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">j</span><span class="p">)</span>
<a name="slacxwfman.py-164"></a>                <span class="bp">self</span><span class="o">.</span><span class="n">update_op</span><span class="p">(</span><span class="n">indx</span><span class="p">,</span><span class="n">op</span><span class="p">)</span>
<a name="slacxwfman.py-165"></a>                <span class="c1"># emit the dataChanged signal</span>
<a name="slacxwfman.py-166"></a>                <span class="c1">#self.dataChanged.emit(QtCore.QModelIndex(),QtCore.QModelIndex()) </span>
<a name="slacxwfman.py-167"></a>                <span class="c1">#self.dataChanged.emit(indx,indx) </span>
<a name="slacxwfman.py-168"></a>                <span class="c1">#outputs_indx = self.index(1,0,indx)</span>
<a name="slacxwfman.py-169"></a>                <span class="c1">#self.dataChanged.emit(outputs_indx,outputs_indx) </span>
<a name="slacxwfman.py-170"></a>                <span class="c1">#outputs_treeitem = item.children[1]</span>
<a name="slacxwfman.py-171"></a>                <span class="c1">#for row in range(len(outputs_treeitem.children)):</span>
<a name="slacxwfman.py-172"></a>                <span class="c1">#    indx = self.index(row,0,outputs_indx)</span>
<a name="slacxwfman.py-173"></a>                <span class="c1">#    self.dataChanged.emit(indx,indx)</span>
<a name="slacxwfman.py-174"></a>            <span class="n">to_run</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">ops_ready</span><span class="p">(</span><span class="n">ops_done</span><span class="p">)</span>
<a name="slacxwfman.py-175"></a>
<a name="slacxwfman.py-176"></a>    <span class="k">def</span> <span class="nf">ops_ready</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class="n">ops_done</span><span class="p">):</span>
<a name="slacxwfman.py-177"></a>        <span class="sd">&quot;&quot;&quot;</span>
<a name="slacxwfman.py-178"></a><span class="sd">        Give a list of indices in self.root_items </span>
<a name="slacxwfman.py-179"></a><span class="sd">        that contain Operations whose inputs are ready</span>
<a name="slacxwfman.py-180"></a><span class="sd">        &quot;&quot;&quot;</span>
<a name="slacxwfman.py-181"></a>        <span class="n">indxs</span> <span class="o">=</span> <span class="p">[]</span>
<a name="slacxwfman.py-182"></a>        <span class="k">for</span> <span class="n">j</span> <span class="ow">in</span> <span class="nb">range</span><span class="p">(</span><span class="nb">len</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">root_items</span><span class="p">)):</span>
<a name="slacxwfman.py-183"></a>            <span class="k">if</span> <span class="ow">not</span> <span class="n">j</span> <span class="ow">in</span> <span class="n">ops_done</span><span class="p">:</span>
<a name="slacxwfman.py-184"></a>                <span class="n">item</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">root_items</span><span class="p">[</span><span class="n">j</span><span class="p">]</span>
<a name="slacxwfman.py-185"></a>                <span class="n">op</span> <span class="o">=</span> <span class="n">item</span><span class="o">.</span><span class="n">data</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span>
<a name="slacxwfman.py-186"></a>                <span class="n">inps</span> <span class="o">=</span> <span class="p">[</span><span class="bp">self</span><span class="o">.</span><span class="n">locate_input</span><span class="p">(</span><span class="n">val</span><span class="p">)</span> <span class="k">for</span> <span class="n">name</span><span class="p">,</span><span class="n">val</span> <span class="ow">in</span> <span class="n">op</span><span class="o">.</span><span class="n">inputs</span><span class="o">.</span><span class="n">items</span><span class="p">()]</span>
<a name="slacxwfman.py-187"></a>                <span class="k">if</span> <span class="ow">not</span> <span class="nb">any</span><span class="p">([</span><span class="n">inp</span> <span class="ow">is</span> <span class="bp">None</span> <span class="k">for</span> <span class="n">inp</span> <span class="ow">in</span> <span class="n">inps</span><span class="p">]):</span>
<a name="slacxwfman.py-188"></a>                    <span class="n">indxs</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">j</span><span class="p">)</span>
<a name="slacxwfman.py-189"></a>        <span class="k">return</span> <span class="n">indxs</span>
<a name="slacxwfman.py-190"></a>
<a name="slacxwfman.py-191"></a>    <span class="k">def</span> <span class="nf">load_wf_dict</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span>
<a name="slacxwfman.py-192"></a>        <span class="sd">&quot;&quot;&quot;</span>
<a name="slacxwfman.py-193"></a><span class="sd">        Build a dask-compatible dictionary from the Operations in this tree</span>
<a name="slacxwfman.py-194"></a><span class="sd">        &quot;&quot;&quot;</span>
<a name="slacxwfman.py-195"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">_wf_dict</span> <span class="o">=</span> <span class="p">{}</span>
<a name="slacxwfman.py-196"></a>        <span class="k">for</span> <span class="n">j</span> <span class="ow">in</span> <span class="nb">range</span><span class="p">(</span><span class="nb">len</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">root_items</span><span class="p">)):</span>
<a name="slacxwfman.py-197"></a>            <span class="n">item</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">root_items</span><span class="p">[</span><span class="n">j</span><span class="p">]</span>
<a name="slacxwfman.py-198"></a>            <span class="c1"># Unpack the Operation</span>
<a name="slacxwfman.py-199"></a>            <span class="n">op</span> <span class="o">=</span> <span class="n">item</span><span class="o">.</span><span class="n">data</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span>
<a name="slacxwfman.py-200"></a>            <span class="n">keyindx</span> <span class="o">=</span> <span class="mi">0</span>
<a name="slacxwfman.py-201"></a>            <span class="n">input_keys</span> <span class="o">=</span> <span class="p">[]</span> 
<a name="slacxwfman.py-202"></a>            <span class="n">input_vals</span> <span class="o">=</span> <span class="p">()</span>
<a name="slacxwfman.py-203"></a>            <span class="k">for</span> <span class="n">name</span><span class="p">,</span><span class="n">val</span> <span class="ow">in</span> <span class="n">op</span><span class="o">.</span><span class="n">inputs</span><span class="o">.</span><span class="n">items</span><span class="p">():</span>
<a name="slacxwfman.py-204"></a>                <span class="c1"># Add a locate_input line for each input </span>
<a name="slacxwfman.py-205"></a>                <span class="n">dask_key</span> <span class="o">=</span> <span class="s1">&#39;op&#39;</span><span class="o">+</span><span class="nb">str</span><span class="p">(</span><span class="n">j</span><span class="p">)</span><span class="o">+</span><span class="s1">&#39;inp&#39;</span><span class="o">+</span><span class="nb">str</span><span class="p">(</span><span class="n">keyindx</span><span class="p">)</span>
<a name="slacxwfman.py-206"></a>                <span class="bp">self</span><span class="o">.</span><span class="n">_wf_dict</span><span class="p">[</span><span class="n">dask_key</span><span class="p">]</span> <span class="o">=</span> <span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">locate_input</span><span class="p">,</span> <span class="n">val</span><span class="p">)</span>
<a name="slacxwfman.py-207"></a>                <span class="n">keyindx</span> <span class="o">+=</span> <span class="mi">1</span>
<a name="slacxwfman.py-208"></a>                <span class="n">input_keys</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">name</span><span class="p">)</span>
<a name="slacxwfman.py-209"></a>                <span class="n">input_vals</span> <span class="o">=</span> <span class="n">input_vals</span> <span class="o">+</span> <span class="p">(</span><span class="n">dask_key</span><span class="p">)</span>
<a name="slacxwfman.py-210"></a>            <span class="c1"># Add a load_inputs line for each op</span>
<a name="slacxwfman.py-211"></a>            <span class="n">dask_key</span> <span class="o">=</span> <span class="s1">&#39;op&#39;</span><span class="o">+</span><span class="nb">str</span><span class="p">(</span><span class="n">j</span><span class="p">)</span><span class="o">+</span><span class="s1">&#39;_load&#39;</span>
<a name="slacxwfman.py-212"></a>            <span class="bp">self</span><span class="o">.</span><span class="n">_wf_dict</span><span class="p">[</span><span class="n">key</span><span class="p">]</span> <span class="o">=</span> <span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">load_inputs</span><span class="p">,</span> <span class="n">op</span><span class="p">,</span> <span class="n">input_keys</span><span class="p">,</span> <span class="n">input_vals</span><span class="p">)</span> 
<a name="slacxwfman.py-213"></a>            <span class="c1"># Add a run_op line for each op</span>
<a name="slacxwfman.py-214"></a>            <span class="n">dask_key</span> <span class="o">=</span> <span class="s1">&#39;op&#39;</span><span class="o">+</span><span class="nb">str</span><span class="p">(</span><span class="n">j</span><span class="p">)</span><span class="o">+</span><span class="s1">&#39;_run&#39;</span>
<a name="slacxwfman.py-215"></a>            <span class="bp">self</span><span class="o">.</span><span class="n">_wf_dict</span><span class="p">[</span><span class="n">key</span><span class="p">]</span> <span class="o">=</span> <span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">run_op</span><span class="p">,</span> <span class="n">op</span><span class="p">)</span> 
<a name="slacxwfman.py-216"></a>
<a name="slacxwfman.py-217"></a>    <span class="nd">@staticmethod</span>
<a name="slacxwfman.py-218"></a>    <span class="k">def</span> <span class="nf">load_inputs</span><span class="p">(</span><span class="n">op</span><span class="p">,</span><span class="n">keys</span><span class="p">,</span><span class="n">vals</span><span class="p">):</span>
<a name="slacxwfman.py-219"></a>        <span class="c1"># fetch Operation at op_row</span>
<a name="slacxwfman.py-220"></a>        <span class="k">for</span> <span class="n">i</span> <span class="ow">in</span> <span class="nb">range</span><span class="p">(</span><span class="nb">len</span><span class="p">(</span><span class="n">keys</span><span class="p">)):</span>
<a name="slacxwfman.py-221"></a>            <span class="n">key</span> <span class="o">=</span> <span class="n">keys</span><span class="p">[</span><span class="n">i</span><span class="p">]</span>
<a name="slacxwfman.py-222"></a>            <span class="n">val</span> <span class="o">=</span> <span class="n">vals</span><span class="p">[</span><span class="n">i</span><span class="p">]</span> 
<a name="slacxwfman.py-223"></a>            <span class="n">op</span><span class="o">.</span><span class="n">inputs</span><span class="p">[</span><span class="n">key</span><span class="p">]</span> <span class="o">=</span> <span class="n">val</span>
<a name="slacxwfman.py-224"></a>        <span class="k">return</span> <span class="n">op</span> 
<a name="slacxwfman.py-225"></a>
<a name="slacxwfman.py-226"></a>    <span class="nd">@staticmethod</span>
<a name="slacxwfman.py-227"></a>    <span class="k">def</span> <span class="nf">run_op</span><span class="p">(</span><span class="n">op</span><span class="p">):</span>
<a name="slacxwfman.py-228"></a>        <span class="k">return</span> <span class="n">op</span><span class="o">.</span><span class="n">run</span><span class="p">()</span>
<a name="slacxwfman.py-229"></a>
<a name="slacxwfman.py-230"></a>    <span class="k">def</span> <span class="nf">locate_input</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span><span class="n">inplocator</span><span class="p">):</span>
<a name="slacxwfman.py-231"></a>        <span class="sd">&quot;&quot;&quot;Return the data pointed to by a given InputLocator object&quot;&quot;&quot;</span>
<a name="slacxwfman.py-232"></a>        <span class="k">if</span> <span class="nb">type</span><span class="p">(</span><span class="n">inplocator</span><span class="p">)</span><span class="o">.</span><span class="n">__name__</span> <span class="o">==</span> <span class="s1">&#39;InputLocator&#39;</span><span class="p">:</span>
<a name="slacxwfman.py-233"></a>            <span class="n">src</span> <span class="o">=</span> <span class="n">inplocator</span><span class="o">.</span><span class="n">src</span>
<a name="slacxwfman.py-234"></a>            <span class="n">val</span> <span class="o">=</span> <span class="n">inplocator</span><span class="o">.</span><span class="n">val</span>
<a name="slacxwfman.py-235"></a>            <span class="k">if</span> <span class="n">src</span> <span class="ow">in</span> <span class="n">optools</span><span class="o">.</span><span class="n">valid_sources</span><span class="p">:</span>
<a name="slacxwfman.py-236"></a>                <span class="k">if</span> <span class="n">src</span> <span class="o">==</span> <span class="n">optools</span><span class="o">.</span><span class="n">text_input</span><span class="p">:</span> 
<a name="slacxwfman.py-237"></a>                    <span class="c1"># val will be already typecast during operation loading- return it directly</span>
<a name="slacxwfman.py-238"></a>                    <span class="k">return</span> <span class="n">val</span> 
<a name="slacxwfman.py-239"></a>                <span class="k">elif</span> <span class="n">src</span> <span class="o">==</span> <span class="n">optools</span><span class="o">.</span><span class="n">image_input</span><span class="p">:</span> 
<a name="slacxwfman.py-240"></a>                    <span class="c1"># follow val as uri in image tree</span>
<a name="slacxwfman.py-241"></a>                    <span class="n">trmod</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">imgman</span>
<a name="slacxwfman.py-242"></a>                <span class="k">elif</span> <span class="n">src</span> <span class="o">==</span> <span class="n">optools</span><span class="o">.</span><span class="n">op_input</span><span class="p">:</span> 
<a name="slacxwfman.py-243"></a>                    <span class="c1"># follow val as uri in workflow tree</span>
<a name="slacxwfman.py-244"></a>                    <span class="n">trmod</span> <span class="o">=</span> <span class="bp">self</span>
<a name="slacxwfman.py-245"></a>                <span class="n">path</span> <span class="o">=</span> <span class="n">val</span><span class="o">.</span><span class="n">split</span><span class="p">(</span><span class="s1">&#39;.&#39;</span><span class="p">)</span>
<a name="slacxwfman.py-246"></a>                <span class="n">parent_indx</span> <span class="o">=</span> <span class="n">QtCore</span><span class="o">.</span><span class="n">QModelIndex</span><span class="p">()</span>
<a name="slacxwfman.py-247"></a>                <span class="k">for</span> <span class="n">itemtag</span> <span class="ow">in</span> <span class="n">path</span><span class="p">:</span>
<a name="slacxwfman.py-248"></a>                    <span class="c1"># get QModelIndex of item from itemtag</span>
<a name="slacxwfman.py-249"></a>                    <span class="n">row</span> <span class="o">=</span> <span class="n">trmod</span><span class="o">.</span><span class="n">list_tags</span><span class="p">(</span><span class="n">parent_indx</span><span class="p">)</span><span class="o">.</span><span class="n">index</span><span class="p">(</span><span class="n">itemtag</span><span class="p">)</span>
<a name="slacxwfman.py-250"></a>                    <span class="n">qindx</span> <span class="o">=</span> <span class="n">trmod</span><span class="o">.</span><span class="n">index</span><span class="p">(</span><span class="n">row</span><span class="p">,</span><span class="mi">0</span><span class="p">,</span><span class="n">parent_indx</span><span class="p">)</span>
<a name="slacxwfman.py-251"></a>                    <span class="c1"># get TreeItem from QModelIndex</span>
<a name="slacxwfman.py-252"></a>                    <span class="n">item</span> <span class="o">=</span> <span class="n">trmod</span><span class="o">.</span><span class="n">get_item</span><span class="p">(</span><span class="n">qindx</span><span class="p">)</span>
<a name="slacxwfman.py-253"></a>                    <span class="c1"># set new parent in case the path continues...</span>
<a name="slacxwfman.py-254"></a>                    <span class="n">parent_indx</span> <span class="o">=</span> <span class="n">qindx</span>
<a name="slacxwfman.py-255"></a>                <span class="c1"># item.data[0] should now be the desired piece of data</span>
<a name="slacxwfman.py-256"></a>                <span class="k">return</span> <span class="n">item</span><span class="o">.</span><span class="n">data</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span>
<a name="slacxwfman.py-257"></a>            <span class="k">else</span><span class="p">:</span> 
<a name="slacxwfman.py-258"></a>                <span class="n">msg</span> <span class="o">=</span> <span class="s1">&#39;found input source {}, should be one of {}&#39;</span><span class="o">.</span><span class="n">format</span><span class="p">(</span>
<a name="slacxwfman.py-259"></a>                <span class="n">src</span><span class="p">,</span> <span class="n">valid_sources</span><span class="p">)</span>
<a name="slacxwfman.py-260"></a>                <span class="k">raise</span> <span class="ne">ValueError</span><span class="p">(</span><span class="n">msg</span><span class="p">)</span>
<a name="slacxwfman.py-261"></a>        <span class="k">else</span><span class="p">:</span>
<a name="slacxwfman.py-262"></a>            <span class="c1"># if this method gets called on an input that is not an InputLocator,</span>
<a name="slacxwfman.py-263"></a>            <span class="c1"># do nothing.</span>
<a name="slacxwfman.py-264"></a>            <span class="k">return</span> <span class="n">inplocator</span>
<a name="slacxwfman.py-265"></a>
</pre></div>
</td></tr></table>
    </div>
  


        </div>
        
      </div>
    </div>
  </div>
  
  <div data-module="source/set-changeset" data-hash="5b763e8d612ceca1e84b0ef52fd4cc673fd4e82a"></div>



  
    
    <script id="branch-dialog-template" type="text/html">
      

<div class="tabbed-filter-widget branch-dialog">
  <div class="tabbed-filter">
    <input placeholder="Filter branches" class="filter-box" autosave="branch-dropdown-20474718" type="text">
    [[^ignoreTags]]
      <div class="aui-tabs horizontal-tabs aui-tabs-disabled filter-tabs">
        <ul class="tabs-menu">
          <li class="menu-item active-tab"><a href="#branches">Branches</a></li>
          <li class="menu-item"><a href="#tags">Tags</a></li>
        </ul>
      </div>
    [[/ignoreTags]]
  </div>
  
    <div class="tab-pane active-pane" id="branches" data-filter-placeholder="Filter branches">
      <ol class="filter-list">
        <li class="empty-msg">No matching branches</li>
        [[#branches]]
          
            [[#hasMultipleHeads]]
              [[#heads]]
                <li class="comprev filter-item">
                  <a class="pjax-trigger filter-item-link" href="/smashml/slacx/src/[[changeset]]/core/workflow/slacxwfman.py?at=[[safeName]]"
                     title="[[name]]">
                    [[name]] ([[shortChangeset]])
                  </a>
                </li>
              [[/heads]]
            [[/hasMultipleHeads]]
            [[^hasMultipleHeads]]
              <li class="comprev filter-item">
                <a class="pjax-trigger filter-item-link" href="/smashml/slacx/src/[[changeset]]/core/workflow/slacxwfman.py?at=[[safeName]]" title="[[name]]">
                  [[name]]
                </a>
              </li>
            [[/hasMultipleHeads]]
          
        [[/branches]]
      </ol>
    </div>
    <div class="tab-pane" id="tags" data-filter-placeholder="Filter tags">
      <ol class="filter-list">
        <li class="empty-msg">No matching tags</li>
        [[#tags]]
          <li class="comprev filter-item">
            <a class="pjax-trigger filter-item-link" href="/smashml/slacx/src/[[changeset]]/core/workflow/slacxwfman.py?at=[[safeName]]" title="[[name]]">
              [[name]]
            </a>
          </li>
        [[/tags]]
      </ol>
    </div>
  
</div>

    </script>
  
  

  </div>

        
        
        
          
    <script id="image-upload-template" type="text/html">
      

<form id="upload-image" method="POST"
    
      action="/xhr/smashml/slacx/image-upload/"
    >
  <input type='hidden' name='csrfmiddlewaretoken' value='nBdFpRnq115QilxmpJgF90dxKluaSCgN' />

  <div class="drop-target">
    <p class="centered">Drag image here</p>
  </div>

  
  <div>
    <button class="aui-button click-target">Select an image</button>
    <input name="file" type="file" class="hidden file-target"
           accept="image/jpeg, image/gif, image/png" />
    <input type="submit" class="hidden">
  </div>
</form>


    </script>
  
        
      </div>
    </div>
  </div>

      </div>
    </div>
  
    </ak-page>
  

  
    
      <footer id="footer" role="contentinfo" data-module="components/footer">
        <section class="footer-body">
          
  <ul>
  <li>
    <a class="support-ga" target="_blank"
       data-support-gaq-page="Blog"
       href="http://blog.bitbucket.org">Blog</a>
  </li>
  <li>
    <a class="support-ga" target="_blank"
       data-support-gaq-page="Home"
       href="/support">Support</a>
  </li>
  <li>
    <a class="support-ga"
       data-support-gaq-page="PlansPricing"
       href="/plans">Plans &amp; pricing</a>
  </li>
  <li>
    <a class="support-ga" target="_blank"
       data-support-gaq-page="DocumentationHome"
       href="//confluence.atlassian.com/display/BITBUCKET">Documentation</a>
  </li>
  <li>
    <a class="support-ga" target="_blank"
       data-support-gaq-page="DocumentationAPI"
       href="//confluence.atlassian.com/x/IYBGDQ">API</a>
  </li>
  <li>
    <a class="support-ga" target="_blank"
       data-support-gaq-page="SiteStatus"
       href="https://status.bitbucket.org/">Site status</a>
  </li>
  <li>
    <a class="support-ga" id="meta-info"
       data-support-gaq-page="MetaInfo"
       href="#">Version info</a>
  </li>
  <li>
    <a class="support-ga" target="_blank"
       data-support-gaq-page="EndUserAgreement"
       href="//www.atlassian.com/legal/customer-agreement?utm_source=bitbucket&amp;utm_medium=link&amp;utm_campaign=footer">Terms of service</a>
  </li>
  <li>
    <a class="support-ga" target="_blank"
       data-support-gaq-page="PrivacyPolicy"
       href="//www.atlassian.com/legal/privacy-policy">Privacy policy</a>
  </li>
</ul>
<div id="meta-info-content" style="display: none;">
  <ul>
    
      <li><a href="/account/user/lensonp/" class="view-language-link">English</a></li>
    
    <li>
      <a class="support-ga" target="_blank"
         data-support-gaq-page="GitDocumentation"
         href="http://git-scm.com/">Git 2.7.4.1.g5468f9e</a>
    </li>
    <li>
      <a class="support-ga" target="_blank"
         data-support-gaq-page="HgDocumentation"
         href="https://www.mercurial-scm.org">Mercurial 3.6.3</a>
    </li>
    <li>
      <a class="support-ga" target="_blank"
         data-support-gaq-page="DjangoDocumentation"
         href="https://www.djangoproject.com/">Django 1.7.11</a>
    </li>
    <li>
      <a class="support-ga" target="_blank"
         data-support-gaq-page="PythonDocumentation"
         href="http://www.python.org/">Python 2.7.3</a>
    </li>
    <li>
      <a class="support-ga" target="_blank"
         data-support-gaq-page="DeployedVersion"
         data-media-hex="4729d131423b"
         href="#">4729d131423b / 4729d131423b @ app-107</a>
    </li>
  </ul>
</div>
<ul class="atlassian-links">
  <li>
    <a id="atlassian-jira-link" target="_blank"
       title="Track everything – bugs, tasks, deadlines, code – and pull reports to stay informed."
       href="https://www.atlassian.com/software/jira/bitbucket-integration?utm_source=bitbucket&amp;utm_medium=link&amp;utm_campaign=bitbucket_footer">JIRA Software</a>
  </li>
  <li>
    <a id="atlassian-confluence-link" target="_blank"
       title="Content Creation, Collaboration & Knowledge Sharing for Teams."
       href="http://www.atlassian.com/software/confluence/overview/team-collaboration-software?utm_source=bitbucket&amp;utm_medium=link&amp;utm_campaign=bitbucket_footer">Confluence</a>
  </li>
  <li>
    <a id="atlassian-bamboo-link" target="_blank"
       title="Continuous integration and deployment, release management."
       href="http://www.atlassian.com/software/bamboo?utm_source=bitbucket&amp;utm_medium=link&amp;utm_campaign=bitbucket_footer">Bamboo</a>
  </li>
  <li>
    <a id="atlassian-sourcetree-link" target="_blank"
       title="A free Git and Mercurial desktop client for Mac or Windows."
       href="http://www.sourcetreeapp.com/?utm_source=bitbucket&amp;utm_medium=link&amp;utm_campaign=bitbucket_footer">SourceTree</a>
  </li>
  <li>
    <a id="atlassian-hipchat-link" target="_blank"
       title="Group chat and IM built for teams."
       href="http://www.hipchat.com/?utm_source=bitbucket&amp;utm_medium=link&amp;utm_campaign=bitbucket_footer">HipChat</a>
  </li>
</ul>
<div id="footer-logo">
  <a target="_blank"
     title="Bitbucket is developed by Atlassian in Austin, San Francisco, and Sydney."
     href="http://www.atlassian.com?utm_source=bitbucket&amp;utm_medium=logo&amp;utm_campaign=bitbucket_footer">Atlassian</a>
</div>

        </section>
      </footer>
    
  
</div>


  

<div data-module="components/mentions/index">
  
    <script id="mention-result" type="text/html">
      
<span class="mention-result">
  <span class="aui-avatar aui-avatar-small mention-result--avatar">
    <span class="aui-avatar-inner">
      <img src="[[avatar_url]]">
    </span>
  </span>
  [[#display_name]]
    <span class="display-name mention-result--display-name">[[&display_name]]</span> <small class="username mention-result--username">[[&username]]</small>
  [[/display_name]]
  [[^display_name]]
    <span class="username mention-result--username">[[&username]]</span>
  [[/display_name]]
  [[#is_teammate]][[^is_team]]
    <span class="aui-lozenge aui-lozenge-complete aui-lozenge-subtle mention-result--lozenge">teammate</span>
  [[/is_team]][[/is_teammate]]
</span>
    </script>
  
  
    <script id="mention-call-to-action" type="text/html">
      
[[^query]]
<li class="bb-typeahead-item">Begin typing to search for a user</li>
[[/query]]
[[#query]]
<li class="bb-typeahead-item">Continue typing to search for a user</li>
[[/query]]

    </script>
  
  
    <script id="mention-no-results" type="text/html">
      
[[^searching]]
<li class="bb-typeahead-item">Found no matching users for <em>[[query]]</em>.</li>
[[/searching]]
[[#searching]]
<li class="bb-typeahead-item bb-typeahead-searching">Searching for <em>[[query]]</em>.</li>
[[/searching]]

    </script>
  
</div>
<div data-module="components/typeahead/emoji/index">
  
    <script id="emoji-result" type="text/html">
      
<div class="aui-avatar aui-avatar-small">
  <div class="aui-avatar-inner">
    <img src="[[src]]">
  </div>
</div>
<span class="name">[[&name]]</span>

    </script>
  
</div>

<div data-module="components/repo-typeahead/index">
  
    <script id="repo-typeahead-result" type="text/html">
      <span class="aui-avatar aui-avatar-project aui-avatar-xsmall">
  <span class="aui-avatar-inner">
    <img src="[[avatar]]">
  </span>
</span>
<span class="owner">[[&owner]]</span>/<span class="slug">[[&slug]]</span>

    </script>
  
</div>

    <script id="share-form-template" type="text/html">
      

<div class="error aui-message hidden">
  <span class="aui-icon icon-error"></span>
  <div class="message"></div>
</div>
<form class="aui">
  <table class="widget bb-list aui">
    <thead>
    <tr class="assistive">
      <th class="user">User</th>
      <th class="role">Role</th>
      <th class="actions">Actions</th>
    </tr>
    </thead>
    <tbody>
      <tr class="form">
        <td colspan="2">
          <input type="text" class="text bb-user-typeahead user-or-email"
                 placeholder="Username or email address"
                 autocomplete="off"
                 data-bb-typeahead-focus="false"
                 [[#disabled]]disabled[[/disabled]]>
        </td>
        <td class="actions">
          <button type="submit" class="aui-button aui-button-light" disabled>Add</button>
        </td>
      </tr>
    </tbody>
  </table>
</form>

    </script>
  

    <script id="share-detail-template" type="text/html">
      

[[#username]]
<td class="user
    [[#hasCustomGroups]]custom-groups[[/hasCustomGroups]]"
    [[#error]]data-error="[[error]]"[[/error]]>
  <div title="[[displayName]]">
    <a href="/[[username]]/" class="user">
      <span class="aui-avatar aui-avatar-xsmall">
        <span class="aui-avatar-inner">
          <img src="[[avatar]]">
        </span>
      </span>
      <span>[[displayName]]</span>
    </a>
  </div>
</td>
[[/username]]
[[^username]]
<td class="email
    [[#hasCustomGroups]]custom-groups[[/hasCustomGroups]]"
    [[#error]]data-error="[[error]]"[[/error]]>
  <div title="[[email]]">
    <span class="aui-icon aui-icon-small aui-iconfont-email"></span>
    [[email]]
  </div>
</td>
[[/username]]
<td class="role
    [[#hasCustomGroups]]custom-groups[[/hasCustomGroups]]">
  <div>
    [[#group]]
      [[#hasCustomGroups]]
        <select class="group [[#noGroupChoices]]hidden[[/noGroupChoices]]">
          [[#groups]]
            <option value="[[slug]]"
                [[#isSelected]]selected[[/isSelected]]>
              [[name]]
            </option>
          [[/groups]]
        </select>
      [[/hasCustomGroups]]
      [[^hasCustomGroups]]
      <label>
        <input type="checkbox" class="admin"
            [[#isAdmin]]checked[[/isAdmin]]>
        Administrator
      </label>
      [[/hasCustomGroups]]
    [[/group]]
    [[^group]]
      <ul>
        <li class="permission aui-lozenge aui-lozenge-complete
            [[^read]]aui-lozenge-subtle[[/read]]"
            data-permission="read">
          read
        </li>
        <li class="permission aui-lozenge aui-lozenge-complete
            [[^write]]aui-lozenge-subtle[[/write]]"
            data-permission="write">
          write
        </li>
        <li class="permission aui-lozenge aui-lozenge-complete
            [[^admin]]aui-lozenge-subtle[[/admin]]"
            data-permission="admin">
          admin
        </li>
      </ul>
    [[/group]]
  </div>
</td>
<td class="actions
    [[#hasCustomGroups]]custom-groups[[/hasCustomGroups]]">
  <div>
    <a href="#" class="delete">
      <span class="aui-icon aui-icon-small aui-iconfont-remove">Delete</span>
    </a>
  </div>
</td>

    </script>
  

    <script id="share-team-template" type="text/html">
      

<div class="clearfix">
  <span class="team-avatar-container">
    <span class="aui-avatar aui-avatar-medium">
      <span class="aui-avatar-inner">
        <img src="[[avatar]]">
      </span>
    </span>
  </span>
  <span class="team-name-container">
    [[display_name]]
  </span>
</div>
<p class="helptext">
  
    Existing users are granted access to this team immediately.
    New users will be sent an invitation.
  
</p>
<div class="share-form"></div>

    </script>
  

    <script id="scope-list-template" type="text/html">
      <ul class="scope-list">
  [[#scopes]]
    <li class="scope-list--item">
      <span class="scope-list--icon aui-icon aui-icon-small [[icon]]"></span>
      <span class="scope-list--description">[[description]]</span>
    </li>
  [[/scopes]]
</ul>

    </script>
  


  


    <script id="source-changeset" type="text/html">
      

<a href="/smashml/slacx/src/[[raw_node]]/[[path]]?at=master"
    class="[[#selected]]highlight[[/selected]]"
    data-hash="[[node]]">
  [[#author.username]]
    <span class="aui-avatar aui-avatar-xsmall">
      <span class="aui-avatar-inner">
        <img src="[[author.avatar]]">
      </span>
    </span>
    <span class="author" title="[[raw_author]]">[[author.display_name]]</span>
  [[/author.username]]
  [[^author.username]]
    <span class="aui-avatar aui-avatar-xsmall">
      <span class="aui-avatar-inner">
        <img src="https://d301sr5gafysq2.cloudfront.net/4729d131423b/img/default_avatar/user_blue.svg">
      </span>
    </span>
    <span class="author unmapped" title="[[raw_author]]">[[author]]</span>
  [[/author.username]]
  <time datetime="[[utctimestamp]]" data-title="true">[[utctimestamp]]</time>
  <span class="message">[[message]]</span>
</a>

    </script>
  

    <script id="embed-template" type="text/html">
      

<form class="aui inline-dialog-embed-dialog">
  <label for="embed-code-[[dialogId]]">Embed this source in another page:</label>
  <input type="text" readonly="true" value="&lt;script src=&quot;[[url]]&quot;&gt;&lt;/script&gt;" id="embed-code-[[dialogId]]" class="embed-code">
</form>

    </script>
  


  
    <script id="edit-form-template" type="text/html">
      


<form class="bb-content-container online-edit-form aui"
      data-repository="[[owner]]/[[slug]]"
      data-destination-repository="[[destinationOwner]]/[[destinationSlug]]"
      data-local-id="[[localID]]"
      [[#isWriter]]data-is-writer="true"[[/isWriter]]
      [[#hasPushAccess]]data-has-push-access="true"[[/hasPushAccess]]
      [[#isPullRequest]]data-is-pull-request="true"[[/isPullRequest]]
      [[#hideCreatePullRequest]]data-hide-create-pull-request="true"[[/hideCreatePullRequest]]
      data-hash="[[hash]]"
      data-branch="[[branch]]"
      data-path="[[path]]"
      data-is-create="[[isCreate]]"
      data-preview-url="/xhr/[[owner]]/[[slug]]/preview/[[hash]]/[[encodedPath]]"
      data-preview-error="We had trouble generating your preview."
      data-unsaved-changes-error="Your changes will be lost. Are you sure you want to leave?">
  <div class="bb-content-container-header">
    <div class="bb-content-container-header-primary">
      <h2 class="bb-content-container-heading">
        [[#isCreate]]
          [[#branch]]
            
              Creating <span class="edit-path">[[path]]</span> on branch: <strong>[[branch]]</strong>
            
          [[/branch]]
          [[^branch]]
            [[#path]]
              
                Creating <span class="edit-path">[[path]]</span>
              
            [[/path]]
            [[^path]]
              
                Creating <span class="edit-path">unnamed file</span>
              
            [[/path]]
          [[/branch]]
        [[/isCreate]]
        [[^isCreate]]
          
            Editing <span class="edit-path">[[path]]</span> on branch: <strong>[[branch]]</strong>
          
        [[/isCreate]]
      </h2>
    </div>
    <div class="bb-content-container-header-secondary">
      <div class="hunk-nav aui-buttons">
        <button class="prev-hunk-button aui-button aui-button-light"
            disabled="disabled" aria-disabled="true"
            title="Previous change">
          <span class="aui-icon aui-icon-small aui-iconfont-up">Previous change</span>
        </button>
        <button class="next-hunk-button aui-button aui-button-light"
            disabled="disabled" aria-disabled="true"
            title="Next change">
          <span class="aui-icon aui-icon-small aui-iconfont-down">Next change</span>
        </button>
      </div>
    </div>
  </div>
  <div class="bb-content-container-body has-header has-footer file-editor">
    <textarea id="id_source"></textarea>
  </div>
  <div class="preview-pane"></div>
  <div class="bb-content-container-footer">
    <div class="bb-content-container-footer-primary">
      <div id="syntax-mode" class="bb-content-container-item field">
        <label for="id_syntax-mode" class="online-edit-form--label">Syntax mode:</label>
        <select id="id_syntax-mode">
          [[#syntaxes]]
            <option value="[[#mime]][[mime]][[/mime]][[^mime]][[mode]][[/mime]]">[[name]]</option>
          [[/syntaxes]]
        </select>
      </div>
      <div id="indent-mode" class="bb-content-container-item field">
        <label for="id_indent-mode" class="online-edit-form--label">Indent mode:</label>
        <select id="id_indent-mode">
          <option value="tabs">Tabs</option>
          <option value="spaces">Spaces</option>
        </select>
      </div>
      <div id="indent-size" class="bb-content-container-item field">
        <label for="id_indent-size" class="online-edit-form--label">Indent size:</label>
        <select id="id_indent-size">
          <option value="2">2</option>
          <option value="4">4</option>
          <option value="8">8</option>
        </select>
      </div>
      <div id="wrap-mode" class="bb-content-container-item field">
        <label for="id_wrap-mode" class="online-edit-form--label">Line wrap:</label>
        <select id="id_wrap-mode">
          <option value="">Off</option>
          <option value="soft">On</option>
        </select>
      </div>
    </div>
    <div class="bb-content-container-footer-secondary">
      [[^isCreate]]
        <button class="preview-button aui-button aui-button-light"
                disabled="disabled" aria-disabled="true"
                data-preview-label="View diff"
                data-edit-label="Edit file">View diff</button>
      [[/isCreate]]
      <button class="save-button aui-button aui-button-primary"
              disabled="disabled" aria-disabled="true">Commit</button>
      [[^isCreate]]
        <a class="aui-button aui-button-link cancel-link" href="#">Cancel</a>
      [[/isCreate]]
    </div>
  </div>
</form>

    </script>
  
  
    <script id="commit-form-template" type="text/html">
      

<form class="aui commit-form"
      data-title="Commit changes"
      [[#isDelete]]
        data-default-message="[[filename]] deleted online with Bitbucket"
      [[/isDelete]]
      [[#isCreate]]
        data-default-message="[[filename]] created online with Bitbucket"
      [[/isCreate]]
      [[^isDelete]]
        [[^isCreate]]
          data-default-message="[[filename]] edited online with Bitbucket"
        [[/isCreate]]
      [[/isDelete]]
      data-fork-error="We had trouble creating your fork."
      data-commit-error="We had trouble committing your changes."
      data-pull-request-error="We had trouble creating your pull request."
      data-update-error="We had trouble updating your pull request."
      data-branch-conflict-error="A branch with that name already exists."
      data-forking-message="Forking repository"
      data-committing-message="Committing changes"
      data-merging-message="Branching and merging changes"
      data-creating-pr-message="Creating pull request"
      data-updating-pr-message="Updating pull request"
      data-cta-label="Commit"
      data-cancel-label="Cancel">
  [[#isDelete]]
    <div class="aui-message info">
      <span class="aui-icon icon-info"></span>
      <span class="message">
        
          Committing this change will delete [[filename]] from your repository.
        
      </span>
    </div>
  [[/isDelete]]
  <div class="aui-message error hidden">
    <span class="aui-icon icon-error"></span>
    <span class="message"></span>
  </div>
  [[^isWriter]]
    <div class="aui-message info">
      <span class="aui-icon icon-info"></span>
      <p class="title">
        
          You don't have write access to this repository.
        
      </p>
      <span class="message">
        
          We'll create a fork for your changes and submit a
          pull request back to this repository.
        
      </span>
    </div>
  [[/isWriter]]
  [[#isRename]]
    <div class="field-group">
      <label for="id_path">New path</label>
      <input type="text" id="id_path" class="text" value="[[path]]"/>
    </div>
  [[/isRename]]
  <div class="field-group">
    <label for="id_message">Commit message</label>
    <textarea id="id_message" class="long-field textarea"></textarea>
  </div>
  [[^isPullRequest]]
    [[#isWriter]]
      <fieldset class="group">
        <div class="checkbox">
          [[#hasPushAccess]]
            [[^hideCreatePullRequest]]
              <input id="id_create-pullrequest" class="checkbox" type="checkbox">
              <label for="id_create-pullrequest">Create a pull request for this change</label>
            [[/hideCreatePullRequest]]
          [[/hasPushAccess]]
          [[^hasPushAccess]]
            <input id="id_create-pullrequest" class="checkbox" type="checkbox" checked="checked" aria-disabled="true" disabled="true">
            <label for="id_create-pullrequest" title="Branch restrictions do not allow you to update this branch.">Create a pull request for this change</label>
          [[/hasPushAccess]]
        </div>
      </fieldset>
      <div id="pr-fields">
        <div id="branch-name-group" class="field-group">
          <label for="id_branch-name">Branch name</label>
          <input type="text" id="id_branch-name" class="text long-field">
        </div>
        

<div class="field-group" id="id_reviewers_group">
  <label for="reviewers">Reviewers</label>

  
  <input id="reviewers" name="reviewers" type="hidden"
          value=""
          data-mention-url="/xhr/mentions/repositories/:dest_username/:dest_slug"
          data-reviewers="[]"
          data-suggested="[]"
          data-locked="[]">

  <div class="error"></div>
  <div class="suggested-reviewers"></div>

</div>

      </div>
    [[/isWriter]]
  [[/isPullRequest]]
  <button type="submit" id="id_submit">Commit</button>
</form>

    </script>
  
  
    <script id="merge-message-template" type="text/html">
      Merged [[hash]] into [[branch]]

[[message]]

    </script>
  
  
    <script id="commit-merge-error-template" type="text/html">
      



  We had trouble merging your changes. We stored them on the <strong>[[branch]]</strong> branch, so feel free to
  <a href="/[[owner]]/[[slug]]/full-commit/[[hash]]/[[path]]?at=[[encodedBranch]]">view them</a> or
  <a href="#" class="create-pull-request-link">create a pull request</a>.


    </script>
  
  
    <script id="selected-reviewer-template" type="text/html">
      <div class="aui-avatar aui-avatar-xsmall">
  <div class="aui-avatar-inner">
    <img src="[[avatar_url]]">
  </div>
</div>
[[display_name]]

    </script>
  
  
    <script id="suggested-reviewer-template" type="text/html">
      <button class="aui-button aui-button-link" type="button" tabindex="-1">[[display_name]]</button>

    </script>
  
  
    <script id="suggested-reviewers-template" type="text/html">
      

<span class="suggested-reviewer-list-label">Recent:</span>
<ul class="suggested-reviewer-list unstyled-list"></ul>

    </script>
  


  
  
  <aui-inline-dialog
    id="help-menu-dialog"
    data-aui-alignment="bottom right"

    
    data-aui-alignment-static="true"
    data-module="header/help-menu"
    responds-to="toggle"
    aria-hidden="true">

  <div id="help-menu-section">
    <h1 class="help-menu-heading">Help</h1>

    <form id="help-menu-search-form" class="aui" target="_blank" method="get"
        action="https://support.atlassian.com/customer/search">
      <span id="help-menu-search-icon" class="aui-icon aui-icon-large aui-iconfont-search"></span>
      <input id="help-menu-search-form-input" name="q" class="text" type="text" placeholder="Ask a question">
    </form>

    <ul id="help-menu-links">
      <li>
        <a class="support-ga" data-support-gaq-page="DocumentationHome"
            href="https://confluence.atlassian.com/x/bgozDQ" target="_blank">
          Online help
        </a>
      </li>
      <li>
        <a class="support-ga" data-support-gaq-page="GitTutorials"
            href="https://www.atlassian.com/git?utm_source=bitbucket&amp;utm_medium=link&amp;utm_campaign=help_dropdown&amp;utm_content=learn_git"
            target="_blank">
          Learn Git
        </a>
      </li>
      <li>
        <a id="keyboard-shortcuts-link"
           href="#">Keyboard shortcuts</a>
      </li>
      <li>
        <a href="/whats-new/" id="features-link">
          Latest features
        </a>
      </li>
      <li>
        <a class="support-ga" data-support-gaq-page="DocumentationTutorials"
            href="https://confluence.atlassian.com/x/Q4sFLQ" target="_blank">
          Bitbucket tutorials
        </a>
      </li>
      <li>
        <a class="support-ga" data-support-gaq-page="SiteStatus"
            href="https://status.bitbucket.org/" target="_blank">
          Site status
        </a>
      </li>
      <li>
        <a class="support-ga" data-support-gaq-page="Home" href="/support">
          Support
        </a>
      </li>
    </ul>
  </div>
</aui-inline-dialog>
  


  <div class="omnibar" data-module="components/omnibar/index">
    <form class="omnibar-form aui"></form>
  </div>
  
    <script id="omnibar-form-template" type="text/html">
      <div class="omnibar-input-container">
  <input class="omnibar-input" type="text" [[#placeholder]]placeholder="[[placeholder]]"[[/placeholder]]>
</div>
<ul class="omnibar-result-group-list"></ul>

    </script>
  
  
    <script id="omnibar-blank-slate-template" type="text/html">
      

<div class="omnibar-blank-slate">No results found</div>

    </script>
  
  
    <script id="omnibar-result-group-list-item-template" type="text/html">
      <div class="omnibar-result-group-header clearfix">
  <h2 class="omnibar-result-group-label" title="[[label]]">[[label]]</h2>
  <span class="omnibar-result-group-context" title="[[context]]">[[context]]</span>
</div>
<ul class="omnibar-result-list unstyled-list"></ul>

    </script>
  
  
    <script id="omnibar-result-list-item-template" type="text/html">
      [[#url]]
  <a href="[[&url]]" class="omnibar-result-label">[[&label]]</a>
[[/url]]
[[^url]]
  <span class="omnibar-result-label">[[&label]]</span>
[[/url]]
[[#context]]
  <span class="omnibar-result-context">[[context]]</span>
[[/context]]

    </script>
  







  
  


<script src="https://d301sr5gafysq2.cloudfront.net/4729d131423b/jsi18n/en/djangojs.js"></script>
<script src="https://d301sr5gafysq2.cloudfront.net/4729d131423b/dist/webpack/vendor.js"></script>
<script src="https://d301sr5gafysq2.cloudfront.net/4729d131423b/dist/webpack/app.js"></script>


<script>
  (function () {
    var ga = document.createElement('script');
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    ga.setAttribute('async', 'true');
    var s = document.getElementsByTagName('script')[0];
    s.parentNode.insertBefore(ga, s);
  }());
</script>
<script async src="https://www.google-analytics.com/analytics.js"></script>

<script type="text/javascript">window.NREUM||(NREUM={});NREUM.info={"beacon":"bam.nr-data.net","queueTime":0,"licenseKey":"a2cef8c3d3","agent":"","transactionName":"Z11RZxdWW0cEVkYLDV4XdUYLVEFdClsdAAtEWkZQDlJBGgRFQhFMQl1DXFcZQ10AQkFYBFlUVlEXWEJHAA==","applicationID":"1841284","errorBeacon":"bam.nr-data.net","applicationTime":151}</script>
</body>
</html>