import numpy as np
import mediapipe as mp
import streamlit as st
import tempfile
from PIL import Image
import os
import cohere
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from gtts import gTTS
from io import BytesIO
from pygame import mixer
#streamlit image input
co = cohere.Client(st.secrets["COHERE_API_KEY"]) # This is your trial API key

st.sidebar.title("Give me an image and I will tell a story on it")
st.title("Image Tale")
img_file=st.sidebar.file_uploader("Upload an image",type=['png','jpg','jpeg'])
def response(objs,gen,temper):
    resp=co.generate(
        model="c4ai-aya-23",
        prompt=str(st.secrets["IMG_TALE"] )+" "+objs+" "+st.secrets["SELECTOR"]+" "+gen+" don't mention any metadata",
        temperature=temper,
        max_tokens=4096,
        stop_sequences=[],
        return_likelihoods='NONE'
    ) 
    return resp.generations[0].text

footer="""<style>
a:link , a:visited{
color: purple;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: black;
color: yellow;
text-align: center;
}
</style>
<div class="footer">
<p>Developed with ❤ by <a style='display: block; text-align: center;' href="https://www.linkedin.com/in/srinadh-vura-85a99b20a/" target="_blank">Srinadh Vura</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)
if img_file is not None:
    tdir=tempfile.TemporaryDirectory()
    tpath=os.path.join(tdir.name,img_file.name)
    with open(tpath,'wb') as f:
        f.write(img_file.getbuffer())
    with st.spinner("Story in baking..."):
        st.sidebar.success("Image uploaded successfully")
        image=Image.open(img_file)
        st.image(image,width=400,caption="Uploaded Image")
        mpimage=mp.Image.create_from_file(tpath)
        # Image detection
        base_options = python.BaseOptions(model_asset_path="./models/efficientdet_lite2.tflite")
        options = vision.ObjectDetectorOptions(base_options=base_options,
                                            score_threshold=0.5)
        detector = vision.ObjectDetector.create_from_options(options)
        res=detector.detect(mpimage)

        objects=[res.detections[i].categories[0].category_name for i in range(len(res.detections))]
        print(objects)
        obj=''
        for i in objects:
            obj=obj+i+', '
        st.sidebar.markdown("---")
        st.sidebar.markdown("## Customize your story")
        lisy=sorted(["Horror","Kids","Comedy","Fiction","Romance","Action","Sci-fi","Thriller","Drama","Crime","Fantasy","Adventure","Animation","Biography","Family","History","Musical","Sport","Western"])
        gen=st.sidebar.selectbox("Select a genre",lisy)
        tem=st.sidebar.select_slider("Select Creativity level",['very low','low','medium','high','very high'])
        clevel={"very low":0.5,"low":0.6,"medium":0.7,"high":0.85,"very high":1.0}
        voice=st.sidebar.radio("Voice?",["Yes","No"])
        st.markdown("---")

        st.sidebar.caption('Note: Vocal output consumes more time')
        submit=st.sidebar.button("Generate Story")

        st.write("### Your story")
        st.markdown("---")
        if submit:
            story=response(obj,gen,clevel[tem])
            if len(objects)==0:
                story=st.secrets["NO_DETECT"]+" "+story
            st.write(story)
            if voice=="Yes":
                tts=gTTS(text=story,lang='en',slow=False, tld='co.in')
                mplay=BytesIO()
                tts.write_to_fp(mplay)
                st.audio(mplay,format='audio/mp3')
            




    



