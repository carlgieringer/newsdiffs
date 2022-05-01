import re

from baseparser import BaseParser
from bs4 import BeautifulSoup


paragraph_wrapper_re = re.compile(r'.*\bStoryBodyCompanionColumn\b.*')

class NYTParser(BaseParser):
    SUFFIX = '?pagewanted=all'
    domains = ['www.nytimes.com']

    feeder_pat   = '^https?://www.nytimes.com/202'
    feeder_pages = ['http://www.nytimes.com/',
                    'http://www.nytimes.com/pages/world/',
                    'http://www.nytimes.com/pages/national/',
                    'http://www.nytimes.com/pages/politics/',
                    'http://www.nytimes.com/pages/nyregion/',
                    'http://www.nytimes.com/pages/business/',
                    'http://www.nytimes.com/pages/technology/',
                    'http://www.nytimes.com/pages/sports/',
                    'http://dealbook.nytimes.com/',
                    'http://www.nytimes.com/pages/science/',
                    'http://www.nytimes.com/pages/health/',
                    'http://www.nytimes.com/pages/arts/',
                    'http://www.nytimes.com/pages/style/',
                    'http://www.nytimes.com/pages/opinion/',
                    'http://www.nytimes.com/pages/automobiles/',
                    'http://www.nytimes.com/pages/books/',
                    'http://www.nytimes.com/crosswords/',
                    'http://www.nytimes.com/pages/dining/',
                    'http://www.nytimes.com/pages/education/',
                    'http://www.nytimes.com/pages/fashion/',
                    'http://www.nytimes.com/pages/garden/',
                    'http://www.nytimes.com/pages/magazine/',
                    'http://www.nytimes.com/pages/business/media/',
                    'http://www.nytimes.com/pages/movies/',
                    'http://www.nytimes.com/pages/arts/music/',
                    'http://www.nytimes.com/pages/obituaries/',
                    'http://www.nytimes.com/pages/realestate/',
                    'http://www.nytimes.com/pages/t-magazine/',
                    'http://www.nytimes.com/pages/arts/television/',
                    'http://www.nytimes.com/pages/theater/',
                    'http://www.nytimes.com/pages/travel/',
                    'http://www.nytimes.com/pages/fashion/weddings/',
                    'http://www.nytimes.com/pages/todayspaper/',
                    'http://topics.nytimes.com/top/opinion/thepubliceditor/']

    def _parse(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        self.meta = soup.findAll('meta')

        seo_title = soup.find('meta', attrs={'name': 'hdl'})
        if seo_title:
            seo_title = seo_title.get('content')
        else:
            seo_title = soup.find('meta', attrs={'property': 'og:title'}).get('content')

        tmp = soup.find('meta', attrs={'name': 'hdl_p'})
        if tmp and tmp.get('content'):
            self.title = tmp.get('content')
        else:
            meta_og_title = soup.find('meta', attrs={'property': 'og:title'})
            if meta_og_title:
                self.title = meta_og_title.get('content')
        if not self.title:
            self.title = seo_title

        try:
            self.date = soup.find('meta', attrs={'name': 'dat'}).get('content')
        except (AttributeError, TypeError):
            try:
                self.date = ' '.join(x.getText() for x in soup.find('time'))
                self.date = self.date.replace('Published ', '')
                if self.date.count(",") == 2:
                    self.date = ",".join(self.date.split(",", 2)[:2])
                if 'Updated' in self.date:
                    self.date = self.date.split('Updated', 1)
                    self.date = self.date[0]
            except (AttributeError, TypeError):
                try:
                    self.date = soup.find('time').getText()
                    self.date = self.date.replace('Published ', '')
                    if self.date.count(",") == 2:
                        self.date = ",".join(self.date.split(",", 2)[:2])
                    if 'Updated' in self.date:
                        self.date = self.date.split('Updated', 1)
                        self.date = self.date[0]
                except (AttributeError, TypeError):
                    try:
                        self.date = soup.find('meta', attrs={'property': 'article:published_time'}).get('content')
                        if self.date.count("T") == 1:
                            self.date = "T".join(self.date.split("T", 1)[:1])
                    except:
                        self.real_article = False
                        return

        try:
            self.byline = soup.find('meta', attrs={'name': 'byl'}).get('content')
        except AttributeError:
            try:
                self.byline = soup.find('p', attrs={'itemprop': 'author creator'}).getText()
            except AttributeError:
                try:
                    self.byline = soup.find('p', attrs={'itemprop': 'author'}).getText()
                except AttributeError:
                    try:
                        self.byline = soup.find('meta', attrs={'name': 'byl'}).get('content')
                    except:
                        self.real_article = False
                        return

        if soup.find('div', attrs={'class': 'live-feed'}):
            live_blog = "YES"
            main_body = "NYT LIVE BLOG - NOT STORED"
        elif soup.find('div', attrs={'class': 'styln-carousel'}) or soup.find('div', attrs={'class': 's-carousel__slides'}) or soup.find('div', attrs={'data-testid': 'photoviewer-wrapper'}):
            body_check = '\n'.join(set(x.getText() for x in soup.findAll('p')))
            body_check = body_check.replace(" The New York Times", "").replace("\n","")
            if body_check == "Advertisement":
                live_blog = "YES"
                main_body = "NYT PHOTO ESSAY - NOT STORED"
            else:
                live_blog = "NO"
        elif soup.find('section', attrs={'class': 'chat-column'}):
            live_blog = "YES"
            main_body = "NYT LIVE STREAM - NOT STORED"
        else:
            live_blog = "NO"

        if live_blog == "NO":
            p_tags = sum([list(soup.findAll('p', attrs=restriction))
                     for restriction in [{'itemprop': 'articleBody'},
                     {'itemprop': 'reviewBody'},
                     {'class': 'story-body-text story-content'}]], [])

            try:
                embed_p_tags = soup.find('div', attrs={'id': 'NYT_MAIN_CONTENT_3_REGION'}).getText()
            except AttributeError:
                embed_p_tags = ''

            try:
                embed_p_tagsa = soup.findAll('div', attrs={'id': 'NYT_MAIN_CONTENT_3_REGION'})[1].getText()
            except IndexError:
                embed_p_tagsa = ''

            try:
                embed_p_tags2 = soup.find('h2', attrs={'id': 'storyline-latest-updates'}).getText()
            except AttributeError:
                embed_p_tags2 = ''

            try:
                embed_p_tags2a = soup.findAll('h2', attrs={'id': 'storyline-latest-updates'})[1].getText()
            except IndexError:
                embed_p_tags2a = ''

            try:
                embed_p_tags3 = soup.find('section', attrs={'role': 'complementary'}).getText()
            except AttributeError:
                embed_p_tags3 = ''

            try:
                embed_p_tags3a = soup.findAll('section', attrs={'role': 'complementary'})[1].getText()
            except IndexError:
                embed_p_tags3a = ''

            try:
                embed_p_tags4 = soup.find('div', attrs={'id': 'NYT_MAIN_CONTENT_2_REGION'}).getText()
            except AttributeError:
                embed_p_tags4 = ''

            try:
                embed_p_tags4a = soup.findAll('div', attrs={'id': 'NYT_MAIN_CONTENT_2_REGION'})[1].getText()
            except IndexError:
                embed_p_tags4a = ''

            try:
                embed_p_tags5 = soup.find('div', attrs={'role': 'complementary'}).getText()
            except AttributeError:
                embed_p_tags5 = ''

            try:
                embed_p_tags5a = soup.findAll('div', attrs={'role': 'complementary'})[1].getText()
            except IndexError:
                embed_p_tags5a = ''

            if not p_tags:
                p_tags = sum([div.findAll(['p', 'h2']) for div in
                             soup.findAll('div', attrs={'class': paragraph_wrapper_re})], [])

            if not p_tags:
                try:
                    article = soup.find('article', attrs={'id': 'story'})
                    article_p_tags = article.findAll('p', 'h2')
                except AttributeError:
                    article = soup.find('article')
                    article_p_tags = article.findAll('p')

                if article.find('header'):
                    header_p_tags = article.find('header').findAll('p')
                else:
                    header_p_tags = ''

                bottom_of_article = article.find('div', attrs={'class': 'bottom-of-article'})

                if header_p_tags == '':
                     p_tags = [p_tag for p_tag in article_p_tags
                               if bottom_of_article not in p_tag.parents  # Remove bottom of article p_tags because we add them as the correction
                               and p_tag.getText() != 'Advertisement']
                else:
                     p_tags = [p_tag for p_tag in article_p_tags
                               if p_tag.getText() and p_tag not in header_p_tags  # Remove header p_tags because it duplicates the title
                               and bottom_of_article not in p_tag.parents  # Remove bottom of article p_tags because we add them as the correction
                               and p_tag.getText() != 'Advertisement']

            div = soup.find('div', attrs={'class': 'story-addendum story-content theme-correction'})
            if div:
                p_tags += [div]

            footer = soup.find('footer', attrs={'class': 'story-footer story-content'})

            if footer:
                p_tags += list(footer.findAll(lambda x: x.get('class') \
                               is not None and 'story-print-citation' \
                               not in x.get('class') and x.name == 'p'))

            main_body = '\n\n'.join([p.getText() for p in p_tags if (p.getText() not in embed_p_tags and 
                   p.getText() not in embed_p_tagsa and
                   p.getText() not in embed_p_tags2 and
                   p.getText() not in embed_p_tags2a and
                   p.getText() not in embed_p_tags3 and
                   p.getText() not in embed_p_tags3a and
                   p.getText() not in embed_p_tags4 and
                   p.getText() not in embed_p_tags4a and
                   p.getText() not in embed_p_tags5 and
                   p.getText() not in embed_p_tags5a)])

        authorids = soup.find('div', attrs={'class': 'authorIdentification'})
        authorid = (authorids.getText() if authorids else '')

        top_correction = '\n'.join(x.getText() for x in
                                   soup.findAll('nyt_correction_top')) or '\n'

        bottom_correction = ''
        correction_bottom_tags = soup.findAll('nyt_correction_bottom')
        if correction_bottom_tags:
            bottom_correction = '\n'.join(x.getText() for x in correction_bottom_tags)
        if not correction_bottom_tags:
            bottom_of_article = soup.find('div', attrs={'class': 'bottom-of-article'})
            if bottom_of_article:
                bottom_correction = bottom_of_article.getText()
                print_info_index = bottom_correction.find('A version of this article appears in print on')
                if print_info_index > -1:
                    bottom_correction = bottom_correction[:print_info_index]
        if not bottom_correction:
            bottom_correction = '\n'

        self.body = '\n'.join([
            top_correction,
            main_body,
            authorid,
            bottom_correction
        ])
