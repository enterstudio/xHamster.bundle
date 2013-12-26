import types, urlparse, re

NAME = 'xHamster'
XH_BASE = 'http://xhamster.com'
XH_CHANNELS = 'http://xhamster.com/'
XH_CHANNEL = 'http://xhamster.com/channels/%s-%s-%s.html'

ART = 'art-default.jpg'
ICON = 'icon-default.png'
ICON_PREFS  = 'icon-prefs.png'
####################################################################################################
def Start():

	ObjectContainer.title1 = NAME
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:23.0) Gecko/20100101 Firefox/23.0'

###################################################################################################
@handler('/video/xhamster', NAME)
def MainMenu():

	oc = ObjectContainer(no_cache=True)

        pageContent = HTML.ElementFromURL(XH_CHANNELS)
        q = pageContent.xpath( "//a/@href[re:test( ., '^\/channels.*\.html', 'i' )]",
             namespaces={"re": "http://exslt.org/regular-expressions"})
        Log.Info( "testing 234")
        getchan = re.compile( r'(.*)-(.*?)\.html')
        
        ## add page for basic latest vids
        titxt = 'New'
        oc.add(DirectoryObject(
			key = Callback(ClipsPage, title=titxt, chanurl='/new', page=1),
			title = titxt
		))
		
        for chan in q:
	        match = getchan.search( chan)
	        if match:
		   basechan = match.group( 1)
                Log.Info( "in loop")
                tit = chan.getparent()
                Log.Info( "jhok1")
                if( tit is types.NoneType ):
		    Log( 'jhnonetit')
		    continue
                titxt = tit.text
                if( titxt is None ):
                    continue
                Log( 'jh tit url: ' + titxt + chan )
                oc.add(DirectoryObject(
			key = Callback(ClipsPage, title=titxt, chanurl=basechan, page=1),
			title = titxt
		))


	return oc

####################################################################################################
@route('/video/xhamster/clipspage')
def ClipsPage(title, chanurl, page=0):

        Log( 'jhzzClipsPage')
	oc = ObjectContainer(title1 = title, title2='Pg:'+str(page), replace_parent=True)
	oc.title1 = title
	Log( 'chanurl: ' + chanurl)
        if ( chanurl == '/new' ) :
	    pageContent = HTML.ElementFromURL( XH_BASE + chanurl + '/' + page + '.html')
	else:
	    pageContent = HTML.ElementFromURL( XH_BASE + chanurl + '-' + page + '.html')
	initialXpath = "//div[@class='video']"
	itemcnt = 0
	nxtpage = 0
	for videoItem in pageContent.xpath(initialXpath):
	        itemcnt += 1
		ht = videoItem.xpath( 'a/@href')
		Log.Info( 'linkage:'+ht[0])
		vtit = videoItem.xpath( 'a/u/@title' )
		videoItemTitle = vtit[0]
		videoItemLink  = videoItem.xpath('a')[0].get('href')
		videoItemThumb = videoItem.xpath('a/img')[0].get('src')		
		vtm = videoItem.xpath( 'a/b')
		duration = vtm[0].text
		#videoItemDuration = GetDurationFromString(duration)
		videoItemRating = (len(videoItem.xpath('img[contains(@src,"/star.gif")]'))+(float(len(videoItem.xpath('img[contains(@src,"/starhalf.gif")]')))/2))*2
		videoItemSummary = 'Duration: ' + duration
		#videoItemSummary += '\r\nRating: ' + str(videoItemRating)
	        Log('videoItemTitle: '+videoItemTitle+' | videoItemLink: '+videoItemLink+' | videoItemThumb: '+videoItemThumb+' | videoItemSummary: '+videoItemSummary)
                #thumb = Resource.ContentsOfURLWithFallback( videoItemThumb)
	        oc.add(VideoClipObject(
	                url = videoItemLink,
			title = videoItemTitle,
			thumb = Resource.ContentsOfURLWithFallback(videoItemThumb)
		))
		
	if itemcnt > 0:
	    nxtpage = int(page) + 1
	    oc.add( DirectoryObject(
			key = Callback(ClipsPage, title=title, chanurl=chanurl, page=nxtpage),
			title = title + ':' + str(nxtpage)
		))
	

	if len(oc) < 1:
		return ObjectContainer(header="Empty", message="This channel doesn't contain any videos.")
	else:
		##oc.objects.sort(key = lambda obj: obj.index)
		return oc
