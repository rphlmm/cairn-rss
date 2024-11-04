* # Table of Contents

* [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#)  
  * [Getting help](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#getting-help)  
* [Quick Start](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#quick-start)  
* [Installing Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup)  
  * [Installing a parser](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser)  
* [Making the soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#making-the-soup)  
* [Kinds of objects](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#kinds-of-objects)  
  * [**`Tag`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#bs4.Tag)**  
    * [**`Tag.name`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#bs4.Tag.name)**  
    * [**`Tag.attrs`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#bs4.Tag.attrs)**  
  * [**`NavigableString`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#bs4.NavigableString)**  
  * [**`BeautifulSoup`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#bs4.BeautifulSoup)**  
  * [Special strings](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#special-strings)  
    * [**`Comment`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#bs4.Comment)**  
    * [For HTML documents](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#for-html-documents)  
      * [**`Stylesheet`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#bs4.Stylesheet)**  
      * [**`Script`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#bs4.Script)**  
      * [**`Template`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#bs4.Template)**  
    * [For XML documents](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#for-xml-documents)  
      * [**`Declaration`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#bs4.Declaration)**  
      * [**`Doctype`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#bs4.Doctype)**  
      * [**`CData`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#bs4.CData)**  
      * [**`ProcessingInstruction`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#bs4.ProcessingInstruction)**  
* [Navigating the tree](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#navigating-the-tree)  
  * [Going down](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#going-down)  
    * [Navigating using tag names](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#navigating-using-tag-names)  
    * [**`.contents`** and **`.children`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#contents-and-children)**  
    * [**`.descendants`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#descendants)**  
    * [**`.string`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#string)**  
    * [**`.strings`** and **`stripped_strings`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#strings-and-stripped-strings)**  
  * [Going up](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#going-up)  
    * [**`.parent`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#parent)**  
    * [**`.parents`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#parents)**  
  * [Going sideways](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#going-sideways)  
    * [**`.next_sibling`** and **`.previous_sibling`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#next-sibling-and-previous-sibling)**  
    * [**`.next_siblings`** and **`.previous_siblings`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#next-siblings-and-previous-siblings)**  
  * [Going back and forth](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#going-back-and-forth)  
    * [**`.next_element`** and **`.previous_element`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#next-element-and-previous-element)**  
    * [**`.next_elements`** and **`.previous_elements`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#next-elements-and-previous-elements)**  
* [Searching the tree](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#searching-the-tree)  
  * [Kinds of filters](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#kinds-of-filters)  
    * [A string](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#a-string)  
    * [A regular expression](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#a-regular-expression)  
    * [**`True`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#true)**  
    * [A function](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#a-function)  
    * [A list](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#a-list)  
  * [**`find_all()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-all)**  
    * [The **`name`** argument](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#the-name-argument)  
    * [The keyword arguments](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#the-keyword-arguments)  
    * [Searching by CSS class](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#searching-by-css-class)  
    * [The **`string`** argument](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#the-string-argument)  
    * [The **`limit`** argument](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#the-limit-argument)  
    * [The **`recursive`** argument](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#the-recursive-argument)  
  * [Calling a tag is like calling **`find_all()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#calling-a-tag-is-like-calling-find-all)**  
  * [**`find()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find)**  
  * [**`find_parents()`** and **`find_parent()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-parents-and-find-parent)**  
  * [**`find_next_siblings()`** and **`find_next_sibling()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-next-siblings-and-find-next-sibling)**  
  * [**`find_previous_siblings()`** and **`find_previous_sibling()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-previous-siblings-and-find-previous-sibling)**  
  * [**`find_all_next()`** and **`find_next()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-all-next-and-find-next)**  
  * [**`find_all_previous()`** and **`find_previous()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-all-previous-and-find-previous)**  
  * [CSS selectors through the **`.css`** property](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#css-selectors-through-the-css-property)  
    * [Advanced Soup Sieve features](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#advanced-soup-sieve-features)  
    * [Namespaces in CSS selectors](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#namespaces-in-css-selectors)  
    * [History of CSS selector support](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#history-of-css-selector-support)  
* [Modifying the tree](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#modifying-the-tree)  
  * [Changing tag names and attributes](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#changing-tag-names-and-attributes)  
  * [Modifying **`.string`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#modifying-string)**  
  * [**`append()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#append)**  
  * [**`extend()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#extend)**  
  * [**`NavigableString()`** and **`.new_tag()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#navigablestring-and-new-tag)**  
  * [**`insert()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#insert)**  
  * [**`insert_before()`** and **`insert_after()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#insert-before-and-insert-after)**  
  * [**`clear()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#clear)**  
  * [**`extract()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#extract)**  
  * [**`decompose()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#decompose)**  
  * [**`replace_with()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#replace-with)**  
  * [**`wrap()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#wrap)**  
  * [**`unwrap()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#unwrap)**  
  * [**`smooth()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#smooth)**  
* [Output](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#output)  
  * [Pretty-printing](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#pretty-printing)  
  * [Non-pretty printing](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#non-pretty-printing)  
  * [Output formatters](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#output-formatters)  
    * [Formatter objects](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#formatter-objects)  
      * [**`HTMLFormatter`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#bs4.HTMLFormatter)**  
      * [**`XMLFormatter`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#bs4.XMLFormatter)**  
    * [Writing your own formatter](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#writing-your-own-formatter)  
  * [**`get_text()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#get-text)**  
* [Specifying the parser to use](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#specifying-the-parser-to-use)  
  * [Differences between parsers](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#differences-between-parsers)  
* [Encodings](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#encodings)  
  * [Output encoding](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#output-encoding)  
  * [Unicode, Dammit](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#unicode-dammit)  
    * [Smart quotes](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#smart-quotes)  
    * [Inconsistent encodings](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#inconsistent-encodings)  
* [Line numbers](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#line-numbers)  
* [Comparing objects for equality](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#comparing-objects-for-equality)  
* [Copying Beautiful Soup objects](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#copying-beautiful-soup-objects)  
* [Advanced parser customization](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#advanced-parser-customization)  
  * [Parsing only part of a document](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#parsing-only-part-of-a-document)  
    * [**`SoupStrainer`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#bs4.SoupStrainer)**  
  * [Customizing multi-valued attributes](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#customizing-multi-valued-attributes)  
  * [Handling duplicate attributes](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#handling-duplicate-attributes)  
  * [Instantiating custom subclasses](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#instantiating-custom-subclasses)  
* [Troubleshooting](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#troubleshooting)  
  * [**`diagnose()`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#diagnose)**  
  * [Errors when parsing a document](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#errors-when-parsing-a-document)  
  * [Version mismatch problems](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#version-mismatch-problems)  
  * [Parsing XML](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#parsing-xml)  
  * [Other parser problems](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#other-parser-problems)  
  * [Miscellaneous](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#miscellaneous)  
  * [Improving Performance](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#improving-performance)  
* [Translating this documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#translating-this-documentation)  
* [Beautiful Soup 3](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#id16)  
  * [Porting code to BS4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#porting-code-to-bs4)  
    * [You need a parser](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#you-need-a-parser)  
    * [Method names](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#method-names)  
    * [Generators](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#generators)  
    * [XML](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#xml)  
    * [Entities](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#entities)  
    * [Miscellaneous](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#id17)

