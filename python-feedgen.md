# Feedgenerator

This module can be used to generate web feeds in both ATOM and RSS
format. It has support for extensions. Included is for example an
extension to produce Podcasts.

It is licensed under the terms of both, the FreeBSD license and the
LGPLv3+. Choose the one which is more convenient for you. For more
details have a look at license.bsd and license.lgpl.

More details about the project:

-   [Repository](https://github.com/lkiesow/python-feedgen)
-   [Documentation](https://lkiesow.github.io/python-feedgen/)
-   [Python Package Index](https://pypi.python.org/pypi/feedgen/)

## Installation

**Prebuild packages**

If your distribution includes this project as package, like Fedora Linux
does, you can simply use your package manager to install the package.
For example:

    $ dnf install python3-feedgen

**Using pip**

You can also use pip to install the feedgen module. Simply run:

    $ pip install feedgen

## Create a Feed

To create a feed simply instantiate the FeedGenerator class and insert
some data:

``` python
from feedgen.feed import FeedGenerator
fg = FeedGenerator()
fg.id('http://lernfunk.de/media/654321')
fg.title('Some Testfeed')
fg.author( {'name':'John Doe','email':'john@example.de'} )
fg.link( href='http://example.com', rel='alternate' )
fg.logo('http://ex.com/logo.jpg')
fg.subtitle('This is a cool feed!')
fg.link( href='http://larskiesow.de/test.atom', rel='self' )
fg.language('en')
```

Note that for the methods which set fields that can occur more than once
in a feed you can use all of the following ways to provide data:

-   Provide the data for that element as keyword arguments
-   Provide the data for that element as dictionary
-   Provide a list of dictionaries with the data for several elements

Example:

``` python
fg.contributor( name='John Doe', email='jdoe@example.com' )
fg.contributor({'name':'John Doe', 'email':'jdoe@example.com'})
fg.contributor([{'name':'John Doe', 'email':'jdoe@example.com'}, ...])
```

## Generate the Feed

After that you can generate both RSS or ATOM by calling the respective
method:

``` python
atomfeed = fg.atom_str(pretty=True) # Get the ATOM feed as string
rssfeed  = fg.rss_str(pretty=True) # Get the RSS feed as string
fg.atom_file('atom.xml') # Write the ATOM feed to a file
fg.rss_file('rss.xml') # Write the RSS feed to a file
```

## Add Feed Entries

To add entries (items) to a feed you need to create new FeedEntry
objects and append them to the list of entries in the FeedGenerator. The
most convenient way to go is to use the FeedGenerator itself for the
instantiation of the FeedEntry object:

``` python
fe = fg.add_entry()
fe.id('http://lernfunk.de/media/654321/1')
fe.title('The First Episode')
fe.link(href="http://lernfunk.de/feed")
```

The FeedGenerator\'s method [add_entry(\...)]{.title-ref} will generate
a new FeedEntry object, automatically append it to the feeds internal
list of entries and return it, so that additional data can be added.

## Extensions

The FeedGenerator supports extensions to include additional data into
the XML structure of the feeds. Extensions can be loaded like this:

``` python
fg.load_extension('someext', atom=True, rss=True)
```

This example would try to load the extension "someext" from the file
[ext/someext.py]{.title-ref}. It is required that
[someext.py]{.title-ref} contains a class named "SomextExtension" which
is required to have at least the two methods
[extend_rss(\...)]{.title-ref} and [extend_atom(\...)]{.title-ref}.
Although not required, it is strongly suggested to use
[BaseExtension]{.title-ref} from [ext/base.py]{.title-ref} as
superclass.

[load_extension(\'someext\', \...)]{.title-ref} will also try to load a
class named "SomextEntryExtension" for every entry of the feed. This
class can be located either in the same file as SomextExtension or in
[ext/someext_entry.py]{.title-ref} which is suggested especially for
large extensions.

The parameters [atom]{.title-ref} and [rss]{.title-ref} control if the
extension is used for ATOM and RSS feeds respectively. The default value
for both parameters is [True]{.title-ref}, meaning the extension is used
for both kinds of feeds.

**Example: Producing a Podcast**

One extension already provided is the podcast extension. A podcast is an
RSS feed with some additional elements for ITunes.

To produce a podcast simply load the [podcast]{.title-ref} extension:

``` python
from feedgen.feed import FeedGenerator
fg = FeedGenerator()
fg.load_extension('podcast')
...
fg.podcast.itunes_category('Technology', 'Podcasting')
...
fe = fg.add_entry()
fe.id('http://lernfunk.de/media/654321/1/file.mp3')
fe.title('The First Episode')
fe.description('Enjoy our first episode.')
fe.enclosure('http://lernfunk.de/media/654321/1/file.mp3', 0, 'audio/mpeg')
...
fg.rss_str(pretty=True)
fg.rss_file('podcast.xml')
```

If the FeedGenerator class is used to load an extension, it is
automatically loaded for every feed entry as well. You can, however,
load an extension for a specific FeedEntry only by calling
[load_extension(\...)]{.title-ref} on that entry.

Even if extensions are loaded, they can be temporarily disabled during
the feed generation by calling the generating method with the keyword
argument [extensions]{.title-ref} set to [False]{.title-ref}.

**Custom Extensions**

If you want to load custom extensions which are not part of the feedgen
package, you can use the method [register_extension]{.title-ref}
instead. You can directly pass the classes for the feed and the entry
extension to this method meaning that you can define them everywhere.

## Testing the Generator

You can test the module by simply executing:

    $ python -m feedgen

If you want to have a look at the code for this test to have a working
code example for a whole feed generation process, you can find it in the
[\_\_main\_\_.py](https://github.com/lkiesow/python-feedgen/blob/master/feedgen/__main__.py).

# [**Module documentation**](https://feedgen.kiesow.be/#id8)

* [**API Documentation**](https://feedgen.kiesow.be/api.html)  
  * [**feedgen**](https://feedgen.kiesow.be/api.html#feedgen)  
  * [**feedgen.feed**](https://feedgen.kiesow.be/api.feed.html)  
  * [**`FeedGenerator`](https://feedgen.kiesow.be/api.feed.html#feedgen.feed.FeedGenerator)**  
  * [**feedgen.entry**](https://feedgen.kiesow.be/api.entry.html)  
  * [**`FeedEntry`](https://feedgen.kiesow.be/api.entry.html#feedgen.entry.FeedEntry)**  
  * [**feedgen.util**](https://feedgen.kiesow.be/api.util.html)  
  * [**`ensure_format()`](https://feedgen.kiesow.be/api.util.html#feedgen.util.ensure_format)**  
  * [**`formatRFC2822()`](https://feedgen.kiesow.be/api.util.html#feedgen.util.formatRFC2822)**  
  * [**feedgen.ext.base**](https://feedgen.kiesow.be/ext/api.ext.base.html)  
  * [**`BaseEntryExtension`](https://feedgen.kiesow.be/ext/api.ext.base.html#feedgen.ext.base.BaseEntryExtension)**  
  * [**`BaseExtension`](https://feedgen.kiesow.be/ext/api.ext.base.html#feedgen.ext.base.BaseExtension)**  
  * [**feedgen.ext.dc**](https://feedgen.kiesow.be/ext/api.ext.dc.html)  
  * [**`DcBaseExtension`](https://feedgen.kiesow.be/ext/api.ext.dc.html#feedgen.ext.dc.DcBaseExtension)**  
  * [**`DcEntryExtension`](https://feedgen.kiesow.be/ext/api.ext.dc.html#feedgen.ext.dc.DcEntryExtension)**  
  * [**`DcExtension`](https://feedgen.kiesow.be/ext/api.ext.dc.html#feedgen.ext.dc.DcExtension)**  
  * [**feedgen.ext.podcast**](https://feedgen.kiesow.be/ext/api.ext.podcast.html)  
  * [**`PodcastExtension`](https://feedgen.kiesow.be/ext/api.ext.podcast.html#feedgen.ext.podcast.PodcastExtension)**  
  * [**feedgen.ext.podcast\_entry**](https://feedgen.kiesow.be/ext/api.ext.podcast_entry.html)  
  * [**`PodcastEntryExtension`](https://feedgen.kiesow.be/ext/api.ext.podcast_entry.html#feedgen.ext.podcast_entry.PodcastEntryExtension)**  
  * [**feedgen.ext.torrent**](https://feedgen.kiesow.be/ext/api.ext.torrent.html)  
  * [**`TorrentEntryExtension`](https://feedgen.kiesow.be/ext/api.ext.torrent.html#feedgen.ext.torrent.TorrentEntryExtension)**  
  * [**`TorrentExtension`](https://feedgen.kiesow.be/ext/api.ext.torrent.html#feedgen.ext.torrent.TorrentExtension)**

# [**Indices and tables**](https://feedgen.kiesow.be/#id9)

* [**Index**](https://feedgen.kiesow.be/genindex.html)  
* [**Module Index**](https://feedgen.kiesow.be/py-modindex.html)  
* [**Search Page**](https://feedgen.kiesow.be/search.html)

