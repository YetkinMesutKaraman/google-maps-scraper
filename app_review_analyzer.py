# import chromedriver_autoinstaller
import pandas as pd
import streamlit as st
import validators

from src.gmaps import Gmaps

# chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
# and if it doesn't exist, download it automatically,
# then add chromedriver to path


TARGET_COLUMNS = ["published_at_date", "rating", "review_text"]


# output_folder = "./scraped_hotels"

if "stage" not in st.session_state:
    st.session_state.stage = 0


def set_stage(stage):
    st.session_state.stage = stage


def is_valid_google_maps_url(url):
    # Google Maps URLs often start with "https://www.google.com/maps/"
    # You can customize this pattern based on your needs
    expected_prefix = "https://www.google.com/maps/place/"

    if not url.startswith(expected_prefix):
        return False

    return validators.url(url)


def validate_url():
    # Get URL input from user
    url_input = st.text_input("Enter the Google Maps Place URL 👇")

    # Button to trigger the action
    st.button("Submit and Validate URL", on_click=set_stage, args=(1,))
    if st.session_state.stage > 0:
        # Check if the entered URL is valid
        if is_valid_google_maps_url(url_input):
            st.success("Valid URL!")

            # Perform further actions with the valid URL (e.g., save to database, fetch data, etc.)
            # In this example, we simply return the URL
            st.write("Valid URL entered:", url_input)
            return url_input

        else:
            st.error("Invalid URL. Please enter a valid URL.")


def get_reviews_data(url_str):
    response_data = Gmaps.links(
        links=[url_str],
        scrape_reviews=True,
        reviews_max=700,
        use_cache=True,
    )
    # if response ok, then create df_reviews
    place_name = response_data["places"][0]["name"]

    place_link = response_data["places"][0]["link"]
    df_reviews = pd.DataFrame(response_data["places"][0]["detailed_reviews"])
    # just use target_columns for further analysis
    df_reviews = df_reviews[TARGET_COLUMNS]
    # df_reviews.head().style

    return df_reviews, place_name, place_link


def filter_reviews_data(df):
    # drop nan review rows
    df.dropna(how="any", subset=["review_text"], inplace=True)
    # filter out short reviews
    st.text("Filter out NaN reviews and too short reviews")
    # print(f"Before filtering: {len(df)} reviews")
    st.write(f"Before filtering: **{len(df)}** reviews")
    short_mask = df["review_text"].apply(lambda row: len(row) > 30)
    df = df[short_mask]
    # print(f"After filtering: {len(df)} reviews")
    st.write(f"After filtering: **{len(df)}** reviews")

    return df


def main():
    st.title("Google Maps Review Analyzer")
    st.text("This app scrapes Google Maps reviews and analyzes them")
    # get user url and validate
    url_str = validate_url()
    # if url_str is valid, then get reviews data
    if url_str:
        # Create a text element and let the reader know the data is loading.
        data_load_state = st.markdown(":rainbow[Loading Data...]")
        df_reviews, place_name, place_link = get_reviews_data(url_str)
        # Notify the reader that the data was successfully loaded.
        data_load_state.markdown(":rainbow[Data loaded]!")
        # filter reviews data
        df_reviews = filter_reviews_data(df_reviews)
        # show place name and link
        st.write(f"**Place Name:** {place_name}")
        st.write(f"**Place Link:** {place_link}")
        # show df_reviews
        st.write(df_reviews.head().style)


if __name__ == "__main__":
    main()
