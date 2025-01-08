import streamlit as st 
from phi.agent import Agent 
from phi.model.google import Gemini 
from phi.tools.duckduckgo import DuckDuckGo
from google.generativeai import upload_file, get_file
import google.generativeai as genai
import os
import time
from pathlib import Path
import tempfile


st.set_page_config(
    page_title='VidWise',
    page_icon='🎥',
    layout='wide'
)


st.title('VidWise 🎥')

st.header('Powered by Google Gemini 1.5 Flash and PhiData')


if 'GOOGLE_API_KEY' not in st.session_state:

    st.session_state.GOOGLE_API_KEY = None



api_key_input = st.text_input(
    "Enter your Google API Key:", 
    type="password", 
    help="This key will be used to access Google Gemini APIs."
)


if st.button("Set API Key"):

    if api_key_input:

        try:

            os.environ["GOOGLE_API_KEY"] = api_key_input
            

            st.session_state.GOOGLE_API_KEY = api_key_input
            

            genai.configure(api_key=api_key_input)

            st.cache_data.clear()

            st.success("API Key set successfully!")

        except Exception as e:

            st.error(f"Failed to configure API Key: {e}")

    else:

        st.warning('No Gemini API key found. Please set your API key in order to proceed further')



if st.session_state.GOOGLE_API_KEY:

    @st.cache_resource
    def initialize_agent():

        return Agent(
            name='Video AI Analyzer',
            model=Gemini(id='gemini-1.5-flash'),
            tools=[DuckDuckGo()],
            markdown=True
        )


    multimodal_agent = initialize_agent()


    video_file_upload = st.file_uploader(
        'Upload your video', 
        type=['mp4', 'mov', 'avi'],
        help='Upload your video for analysis'
    )


    if video_file_upload:

        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:

            temp_video.write(video_file_upload.read())

            video_path = temp_video.name


        st.video(video_path, format='video/mp4', start_time=0)


        user_question = st.text_area(
            'What insights are you seeking from this video?',
            placeholder='Ask anything about the video content.',
            help='Provide specific content or insights you want from the video.'
        )


        if st.button('🔍 Analyze Video', key='analyze_video_button'):

            if not user_question:

                st.warning('Please enter your question')

            else:

                try:

                    with st.spinner('Processing video and gathering insights...'):


                        processed_video = upload_file(video_path)


                        while processed_video.state.name == 'PROCESSING':

                            time.sleep(1)

                            processed_video = get_file(processed_video.name)


                        analysis_prompt = (
                            f"""
                            Analyze the uploaded video for content and context.
                            Respond to the following query using video insights and supplementary web research:
                            {user_question}

                            Provide a detailed, user-friendly, and actionable response.
                            """
                        )


                        res = multimodal_agent.run(analysis_prompt, videos=[processed_video])


                    st.subheader("Analysis Result")

                    st.markdown(res.content)


                except Exception as error:

                    st.error(f"An error occurred during analysis: {error}")

                finally:

                    Path(video_path).unlink(missing_ok=True)


    else:

        st.info("Upload a video file to begin analysis.")

else:

    st.info("Please set your Google API Key to proceed.")
