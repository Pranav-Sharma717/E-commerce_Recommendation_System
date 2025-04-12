from flask import Flask, request, render_template
import pandas as pd
import random
from flask_sqlalchemy import SQLAlchemy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# load files===========================================================================================================
trending_products = pd.read_csv("C:/Users/gvpra/Downloads/Ecommerce_Recommendation_System/E-commerce_Recommendation_System/P-2.1/models/trending_products.csv")
train_data = pd.read_csv("C:/Users/gvpra/Downloads/Ecommerce_Recommendation_System/E-commerce_Recommendation_System/P-2.1/models/clean_data.csv")
print(train_data['Name'].head(5))

# database configuration---------------------------------------
app.secret_key = "alskdjfwoeieiurlskdjfslkdjf"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/ecomm"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Define your model class for the 'signup' table
class Signup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Define your model class for the 'signup' table
class Signin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)


# Recommendations functions============================================================================================
# Function to truncate product name
def truncate(text, length):
    if len(text) > length:
        return text[:length] + "..."
    else:
        return text


# def content_based_recommendations(train_data, item_name, top_n=10):
#     # Check if the item name exists in the training data
#     normalized_names = train_data['Name'].str.lower().str.strip()
#     if item_name.lower().strip() not in normalized_names.values:
#         print(f"❌ Item '{item_name}' not found (case-insensitive match).")
#         return pd.DataFrame()


#     # Create a TF-IDF vectorizer for item descriptions
#     tfidf_vectorizer = TfidfVectorizer(stop_words='english')

#     # Apply TF-IDF vectorization to item descriptions
#     tfidf_matrix_content = tfidf_vectorizer.fit_transform(train_data['Tags'])

#     # Calculate cosine similarity between items based on descriptions
#     cosine_similarities_content = cosine_similarity(tfidf_matrix_content, tfidf_matrix_content)

#     # Find the index of the item
#     item_index = train_data[normalized_names == item_name.lower().strip()].index[0]

#     # Get the cosine similarity scores for the item
#     similar_items = list(enumerate(cosine_similarities_content[item_index]))

#     # Sort similar items by similarity score in descending order
#     similar_items = sorted(similar_items, key=lambda x: x[1], reverse=True)

#     # Get the top N most similar items (excluding the item itself)
#     top_similar_items = similar_items[1:top_n+1]

#     # Get the indices of the top similar items
#     recommended_item_indices = [x[0] for x in top_similar_items]

#     # Get the details of the top similar items
#     recommended_items_details = train_data.iloc[recommended_item_indices][['Name', 'ReviewCount', 'Brand', 'ImageURL', 'Rating']]

#     return recommended_items_details
def content_based_recommendations(train_data, item_name, top_n=10):
    # Case-insensitive partial match lookup
    matches = train_data[train_data['Name'].str.contains(item_name, case=False, na=False)]

    if matches.empty:
        print(f"❌ Item '{item_name}' not found (case-insensitive match).")
        return pd.DataFrame()

    # Take the first matching index
    item_index = matches.index[0]

    # TF-IDF vectorizer for product tags
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix_content = tfidf_vectorizer.fit_transform(train_data['Tags'])

    cosine_similarities_content = cosine_similarity(tfidf_matrix_content, tfidf_matrix_content)

    # Get cosine similarity scores for the matched item
    similar_items = list(enumerate(cosine_similarities_content[item_index]))
    similar_items = sorted(similar_items, key=lambda x: x[1], reverse=True)

    # Get top N recommendations (excluding the item itself)
    top_similar_items = similar_items[1:top_n+1]
    recommended_item_indices = [x[0] for x in top_similar_items]

    # Extract details
    recommended_items_details = train_data.iloc[recommended_item_indices][['Name', 'ReviewCount', 'Brand', 'ImageURL', 'Rating']]
    return recommended_items_details

# routes===============================================================================
# List of predefined image URLs
random_image_urls = [
    ###Apply Images from Dhruv
    "C:/Users/gvpra/Downloads/Ecommerce_Recommendation_System/E-commerce_Recommendation_System/P-2.1/static/assets-1/img/kokie lipstick.jpeg",
    "static/img/img_2.png",
    "static/img/img_3.png",
    "static/img/img_4.png",
    "static/img/img_5.png",
    "static/img/img_6.png",
    "static/img/img_7.png",
    "static/img/img_8.png",
]


@app.route("/")
def index():
    # Create a list of random image URLs for each product
    random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
    price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
    return render_template('index.html',trending_products=trending_products.head(8),truncate = truncate,
                           random_product_image_urls=random_product_image_urls,
                           random_price = [random.choice(price) for _ in range(len(trending_products.head(8)))]
)

@app.route("/main")
def main():
    print("Main page route hit!")
    return render_template('main.html', content_based_rec=[], truncate=truncate,
                           random_product_image_urls=[], random_price=[])



# routes
@app.route("/index")
def indexredirect():
    # Create a list of random image URLs for each product
    random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
    price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
    return render_template('index.html', trending_products=trending_products.head(8), truncate=truncate,
                           random_product_image_urls=random_product_image_urls,
                           random_price=random.choice(price))

@app.route("/signup", methods=['POST','GET'])
def signup():
    if request.method=='POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        new_signup = Signup(username=username, email=email, password=password)
        db.session.add(new_signup)
        db.session.commit()

        # Create a list of random image URLs for each product
        random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
        price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
        return render_template('index.html', trending_products=trending_products.head(8), truncate=truncate,
                               random_product_image_urls=random_product_image_urls, random_price=random.choice(price),
                               signup_message='User signed up successfully!'
                               )

# Route for signup page
@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if request.method == 'POST':
        username = request.form['signinUsername']
        password = request.form['signinPassword']
        new_signup = Signin(username=username,password=password)
        db.session.add(new_signup)
        db.session.commit()

        # Create a list of random image URLs for each product
        random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
        price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
        return render_template('index.html', trending_products=trending_products.head(8), truncate=truncate,
                               random_product_image_urls=random_product_image_urls, random_price=random.choice(price),
                               signup_message='User signed in successfully!'
                               )
# @app.route("/recommendations", methods=['POST', 'GET'])


# @app.route("/recommendations", methods=['POST', 'GET'])
# def recommendations():
#     if request.method == 'POST':
#         prod = request.form.get('prod')
#         nbr_input = request.form.get('nbr')
#         nbr = int(nbr_input) if nbr_input and nbr_input.isdigit() else 5

#         print("🔍 Product received:", prod)
#         print("🔢 Recommendations requested:", nbr)

#         content_based_rec = content_based_recommendations(train_data, prod, top_n=nbr)

#         if content_based_rec.empty:
#             message = "No recommendations available for this product."
#             return render_template('main.html', message=message)
#         else:
#             random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(content_based_rec))]
#             price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
#             random_price = [random.choice(price) for _ in range(len(content_based_rec))]

#             return render_template('main.html',
#                                    content_based_rec=content_based_rec,
#                                    truncate=truncate,
#                                    random_product_image_urls=random_product_image_urls,
#                                    random_price=random_price)
@app.route("/recommendations", methods=['POST', 'GET'])
def recommendations():
    if request.method == 'POST':
        prod = request.form.get('prod')
        nbr_input = request.form.get('nbr')
        nbr = int(nbr_input) if nbr_input and nbr_input.isdigit() else 5

        print(f"🔍 Product received: {prod}")
        print(f"🔢 Recommendations requested: {nbr}")

        content_based_rec = content_based_recommendations(train_data, prod, top_n=nbr)

        if content_based_rec.empty:
            message = f"No recommendations available for '{prod}'."
            return render_template('main.html', message=message, content_based_rec=[],
                                   random_product_image_urls=[], random_price=[], truncate=truncate)

        # Generate dummy image URLs and prices
        random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(content_based_rec))]
        price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
        random_price = [random.choice(price) for _ in range(len(content_based_rec))]


        return render_template('main.html',
                               content_based_rec=content_based_rec,
                               truncate=truncate,
                               random_product_image_urls=random_product_image_urls,
                               random_price=random_price)





if __name__=='__main__':
    app.run(debug=True)