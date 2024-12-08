import streamlit as st
from openai import OpenAI
import pandas as pd

st.title("Azu Bot: English-to-Japanese Translator")

# Sidebar for API Key
st.sidebar.title("API Key")
api_key = st.sidebar.text_input("Enter your OpenAI API Key")

# Validate API Key
if not api_key:
    st.warning("Please enter your OpenAI API Key in the sidebar.")
    st.stop()

# Set OpenAI API key
client = OpenAI(api_key=api_key)

# User Input
english_text = st.text_area("Enter English sentences to translate:", placeholder="ใส่ข้อความภาษาอังกฤษที่นี่...")

if st.button("Translate and Extract Vocabulary"):
    if english_text.strip() == "":
        st.warning("Please enter some English text.")
        st.stop()

    with st.spinner("Processing..."):
        # Translation and Vocabulary Extraction
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Translate the following English text to Japanese:\n\n"
                            f"{english_text}\n\n"
                            f"Then identify interesting vocabulary from the Japanese translation. "
                            f"First, provide the full Japanese translation as plain text. "
                            f"Then, provide the vocabulary as a table in the following format:\n\n"
                            f"Vocabulary | Translation | Example Sentence Using the Word\n\n"
                            f"Separate each column with a '|' character and use new lines for each vocabulary entry."
                        ),
                    }
                ],
            )
            result = response.choices[0].message.content

            # Split the response into translation and vocabulary
            parts = result.split("\n\n", 1)
            translation = parts[0].strip() if len(parts) > 0 else "No translation provided."
            vocabulary_section = parts[1].strip() if len(parts) > 1 else ""

            # Display the Japanese translation
            st.markdown("### Translation")
            st.write(translation)

            # Parse vocabulary into DataFrame
            rows = []
            for line in vocabulary_section.split("\n"):
                if "|" in line:
                    parts = [col.strip() for col in line.split("|")]
                    if len(parts) == 3:
                        rows.append({
                            "Vocabulary": parts[1], 
                            "Translation": parts[0], 
                            "Example Sentence Using the Word": parts[2]
                        })
            
            rows = rows[1:]

            # Create the DataFrame
            if rows:
                df = pd.DataFrame(rows)
                st.markdown("### Interesting Vocabulary")
                st.dataframe(df)

                # Download as CSV
                @st.cache_data
                def convert_df_to_csv(dataframe):
                    return dataframe.to_csv(index=False).encode("utf-8")

                csv = convert_df_to_csv(df)
                st.download_button(
                    label="Download Vocabulary as CSV",
                    data=csv,
                    file_name="vocabulary_extraction.csv",
                    mime="text/csv",
                )
                st.markdown("*Open csv file using sheets. Excel is not compatible.")
            else:
                st.warning("No vocabulary was extracted. Please check the input or try again.")

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
