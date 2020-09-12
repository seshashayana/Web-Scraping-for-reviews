from flask import Flask, render_template, request
import bs4 as bs
import urllib.request as urlClient

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/present_reviews', methods=['POST'])
def present_reviews():
    try:
        search_text = request.form['search_text']
        search_site = request.form['submit_button']
        searchstring = search_text.replace(" ", "+")  # Getting the search text from the index page
        product = search_text
        flipkart_url = "https://www.flipkart.com/search?q="  # Define the Flipkart URL to scrap data
        amazon_url = "https://www.amazon.in/s?k="
        if search_site == "Search Amazon":
            reviews = search_amazon(search_text, amazon_url)
        elif search_site == "Search Flipkart":
            reviews = search_flipkart(search_text, flipkart_url)
        return render_template('present_reviews.html', reviews=reviews, product=product)
    except Exception as e:
        print(e)
        return render_template('index.html')


def search_amazon(search_text, url):
    url = url
    # Replace the Search String Empty Spaces with '+' to avoid blank spaces in the url
    search_for = search_text.replace(" ", "+")
    url = url + search_for

    # Pharse the WebPage to collect data in machine readable format
    req = urlClient.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = urlClient.urlopen(req)
    soup = bs.BeautifulSoup(res, 'html.parser')

    # Collect the links to the listed items in the search output web-page
    # Have addded try except to avoid errorsin case amazon web-search does not result in valid outputs
    try:
        all_links = soup.find_all('a', attrs={'class': 'a-link-normal a-text-normal'})
        links_list = []
        for links in all_links:
            links_list.append(links.get('href'))
    except Exception as e:
        print("Something went wrong \n", e)

    # initialize the reviews list
    reviews = []
    for link in links_list:
        if len(reviews) >= 50:
            break
        else:
            # Pick first link for scraping reviews
            curr_link = "https://www.amazon.in" + link

            # Pharse the Product WebPage to collect data in machine readable format
            req = urlClient.Request(curr_link, headers={'User-Agent': 'Mozilla/5.0'})
            res = urlClient.urlopen(req)
            soup = bs.BeautifulSoup(res, 'html.parser')

            # Collect the links to the listed items in the search output web-page
            containers = soup.find_all('div', {'class': 'a-section celwidget'})

            # Scrape for the required data and collect in a dictionary to append into reviews list
            for container in containers:
                try:
                    name_box = container.div.a.find_all('div')[-1]
                    name = str(name_box.span.text)
                except Exception as e:
                    print("Couldn't locate name \n" + str(e))

                try:
                    rate_box = container.find_all('div')[4]
                    rating = str(rate_box.a.get('title'))
                except Exception as e:
                    print("Couldn't locate rating \n" + str(e))

                try:
                    rate_box = container.find_all('div')[4]
                    tag_box = rate_box.find_all('a')[1]
                    comment_tag = str(tag_box.span.text)
                except Exception as e:
                    print("Couldn't locate name \n" + str(e))

                try:
                    comment_box = container.find_all('div')[8]
                    comment = str(comment_box.span.text)
                except Exception as e:
                    print("Couldn't locate rating \n" + str(e))

                my_dict = {'Name': name, 'Rating': rating, 'Tag': comment_tag, 'Comment': comment}
                reviews.append(my_dict)
    # Save the reviews table into a csv file helping in easy readability
    # review_table = pd.DataFrame(reviews, index=range(len(reviews)))
    # review_table.to_csv(r'Reviews_Amazon.csv', index=False)
    return reviews


def search_flipkart(search_text, url):
    url = url
    # Replace the Search String Empty Spaces with '+' to avoid blank spaces in the url
    search_for = search_text.replace(" ", "+")
    url = url + search_for

    # Pharse the WebPage to collect data in machine readable format
    req = urlClient.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = urlClient.urlopen(req)
    soup = bs.BeautifulSoup(res, 'html.parser')

    # Collect the links to the listed items in the search output web-page
    # Have added try except to avoid errors in case amazon web-search does not result in valid outputs
    try:
        all_links = soup.find_all('div', {'class': 'bhgxx2 col-12-12'})
        del all_links[0:3]
        all_links = all_links[:len(all_links) - 4]
        links_list = []
        for link in all_links:
            links_list.append(link.div.div.div.a['href'])
    except Exception as e:
        print("Something went wrong \n", e)

    # initialize the reviews list
    reviews = []
    for link in links_list:
        if len(reviews) >= 50:
            break
        else:
            curr_link = str("https://www.flipkart.com" + link)

            # Pharse the Product WebPage to collect data in machine readable format
            req = urlClient.Request(curr_link, headers={'User-Agent': 'Mozilla/5.0'})
            res = urlClient.urlopen(req)
            soup = bs.BeautifulSoup(res, 'html.parser')

            # Collect the links to the listed items in the search output web-page
            containers = soup.find_all('div', {'class': '_3nrCtb'})

            # Scrape for the required data and collect in a dictionary to append into reviews list
            for container in containers:
                try:
                    name = container.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                except Exception as e:
                    print("Couldn't locate name \n" + str(e))

                try:
                    rating = container.div.div.div.div.text
                    rating = str(rating)+".0 of 5.0"
                except Exception as e:
                    print("Couldn't locate rating \n" + str(e))

                try:
                    comment_tag = container.div.div.div.p.text
                except Exception as e:
                    print("Couldn't locate name \n" + str(e))

                try:
                    comment_box = container.div.div.find_all('div', {'class': ''})
                    comment = str(comment_box[0].div.text)
                except Exception as e:
                    print("Couldn't locate rating \n" + str(e))

                my_dict = {'Name': name, 'Rating': rating, 'Tag': comment_tag, 'Comment': comment}
                reviews.append(my_dict)
    # Save the reviews table into a csv file helping in easy readability
    # review_table = pd.DataFrame(reviews, index=range(len(reviews)))
    # review_table.to_csv(r'Reviews_Flipkart.csv', index=False)
    return reviews


if __name__ == '__main__':
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
