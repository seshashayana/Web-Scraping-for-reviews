# Importing all necessary libraries
# Flask, BeautifulSoup, Urllib, Flask-Cors
from flask import Flask, render_template, request
import bs4 as bs
import urllib.request as urlclient
from flask_cors import CORS, cross_origin

# Defining the Flask Application
app = Flask(__name__)
CORS(app)


# Creating initial routing / homepage
# Displays the home page as soon as the base url is clicked
@app.route('/', methods=['GET'])
@cross_origin()
def index():
    return render_template('index.html')


# Creating the routing to display the results once the search button on index page is clicked
@app.route('/present_reviews', methods=['GET', 'POST'])
@cross_origin()
def present_reviews():
    try:
        # Obtain the product name to search reviews
        search_text = request.form['search_text']
        searchstring = search_text.replace(" ", "+")
        product = search_text

        # Define the search url link
        flipkart_url = "https://www.flipkart.com/search?q="
        url = flipkart_url + searchstring

        # identify the link and phrase the webpage to collect data in machine readable format
        req = urlclient.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urlclient.urlopen(req)
        soup = bs.BeautifulSoup(res, 'html.parser')

        # Collect the links of the displayed products
        # Have addded try except to avoid errors in case flipkart web-search does not result in valid outputs
        try:
            all_links = soup.find_all('div', attrs={'class': 'bhgxx2 col-12-12'})
            del all_links[0:3]
            all_links = all_links[:len(all_links) - 4]
            link_list = []
            for link in all_links:
                link_list.append(link.div.div.div.a['href'])
        except Exception as e:
            print("Something went wrong \n", e)

        # Once we have the product list, we can iterate through products to scrape the reviews
        # Prepare an empty list called reviews
        reviews = []
        for link in link_list:
            if len(reviews) >= 50:
                break
            else:
                curr_link = str("https://www.flipkart.com" + link)

                # Pharse the Product WebPage to collect data in machine readable format
                req = urlclient.Request(curr_link, headers={'User-Agent': 'Mozilla/5.0'})
                res = urlclient.urlopen(req)
                soup = bs.BeautifulSoup(res, 'html.parser')

                # Pick the product name from the selected link
                product_name = soup.find('h1', {'class': '_9E25nV'})
                product_name = product_name.span.text

                # Collect the links to the listed items in the search output web-page
                containers = soup.find_all('div', {'class': '_3nrCtb'})
                del containers[-1]
                # Scrape for the required data and collect in a dictionary to append into reviews list
                for container in containers:
                    try:
                        name = container.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                    except Exception as e:
                        print("Couldn't locate name \n" + str(e))

                    try:
                        rating = container.div.div.div.div.text
                        rating = str(rating) + ".0 of 5.0"
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

                    my_dict = {'Product Name': product_name, 'Name': name, 'Rating': rating, 'Tag': comment_tag, 'Comment': comment}
                    reviews.append(my_dict)
        return render_template('present_reviews.html', reviews=reviews, product=product)
    except Exception as e:
        print("Something went wrong \n", e)


@app.route('/read_me', methods=['GET', 'POST'])
@cross_origin()
def read_me():
    return render_template('read_me.html')


if __name__ == '__main__':
    app.run(debug=True)