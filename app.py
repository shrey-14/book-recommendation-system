import gradio as gr
import pickle
import numpy as np

# Load the pre-trained data and models
popular_df = pickle.load(open("popular.pkl", "rb"))
pt = pickle.load(open("pt.pkl", "rb"))
books = pickle.load(open("books.pkl", "rb"))
similarity_score = pickle.load(open("similarity_scores.pkl", "rb"))
pt_index_list = pickle.load(open("pt_index_list.pkl", "rb"))

# Function to display the top 50 books


def display_top_50_books():
    book_names = popular_df["Book-Title"].values
    authors = popular_df["Book-Author"].values
    images = popular_df["Image-URL-L"].values
    votes = popular_df["num_ratings"].values
    ratings = popular_df["avg_rating"].round(2).values

    
    book_cards = '<div style="display: flex; flex-wrap: wrap; justify-content: space-between; margin: 10px 0;">'
    for i in range(len(book_names)):
            book_cards += f"""
            <div style="flex: 1 1 calc(25% - 100px); height: 570px; margin: 20px 10px; border-radius: 8px; overflow: hidden; border: 1px solid #ddd; box-sizing: border-box;">
                <img src="{images[i]}" alt="Book Image" style="width: 100%; height: 70%;">
                <div style="padding: 10px;">
                    <h3 style="font-size: 16px; margin: 5px 0; font-weight: bold;">{book_names[i]}</h3>
                    <p style="font-size: 14px; margin: 5px 0; font-style: italic;">By: {authors[i]}</p>
                    <p style="font-size: 14px; margin: 5px 0; font-weight: bold;">Votes: {votes[i]}</p>
                    <p style="font-size: 14px; margin: 5px 0; font-weight: bold;">Rating: {ratings[i]}</p>
                </div>
            </div>
            """
    book_cards += '</div>'
    return book_cards

# Function to recommend books based on user input


def recommend_books(user_input):
    index = np.where(pt.index == user_input)[0][0]
    distances = similarity_score[index]
    similar_items = list(
        sorted(enumerate(distances), reverse=True, key=lambda x: x[1])[1:5])

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books["Book-Title"] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates(
            "Book-Title")["Book-Title"].values))
        item.extend(list(temp_df.drop_duplicates(
            "Book-Title")["Book-Author"].values))
        item.extend(list(temp_df.drop_duplicates(
            "Book-Title")["Image-URL-L"].values))
        data.append(item)

    return data

# Gradio interface for the top 50 books


def top_50_books_interface():
    books = display_top_50_books()
    return gr.update(value=books)

# Gradio interface for recommending books


def recommend_interface(book_title):
    recommendations = recommend_books(book_title)
    rec_cards = '<div style="display: flex;justify-content: space-between;padding: 20px;margin: 0 auto;max-width: 100%">'
    for rec in recommendations:
        rec_cards += f"""
            <div style="width:280px !important; height: 520px !important; margin: 0 10px;border: 1px solid #ddd;border-radius: 8px;overflow: hidden; ">
                <img src={ rec[2] } alt="Book 1" style="width: 100%; height: 370px; display: block">
                <div style="padding: 15px; height: 130px;">
                    <div style="font-size: 18px;font-weight: bold;margin: 10px 0;">{ rec[0] }</div>
                    <div style="font-size: 16px; font-style:italic;">By: { rec[1] }</div>
                </div>
            </div>
          """
    rec_cards += "</div>"
    return gr.update(value=rec_cards)


# Create Gradio components
book_dropdown = gr.Dropdown(
    choices=pt_index_list, label="Choose a book")
recommend_button = gr.Button("Recommend")
top_50_button = gr.Button("Show Top 50 Books")
top_50_output = gr.HTML()
recommend_output = gr.HTML()

# Create Gradio interface
with gr.Blocks() as demo:

    with gr.Tab("Top 50 Books"):
        gr.Markdown("# Top 50 Books")
        top_50_button.render()
        top_50_button.click(fn=top_50_books_interface, outputs=top_50_output)
        top_50_output.render()

    with gr.Tab("Recommend Books"):
        gr.Markdown("# Recommend Books")
        book_dropdown.render()
        recommend_button.render()
        recommend_button.click(fn=recommend_interface,
                               inputs=book_dropdown, outputs=recommend_output)
        recommend_output.render()

# Launch Gradio app
if __name__ == '__main__':
    demo.launch()
