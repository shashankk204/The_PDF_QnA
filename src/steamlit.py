import streamlit as st
from src.model import create_embedding,create_final_message_state


def app():


    
    st.set_page_config(page_title="Chatbot", layout="centered")
    st.title(" PDF SUMMERIZER",)
    pdf=st.file_uploader(label="Upload your PDF file:",accept_multiple_files=False,type=["pdf"])




    if(pdf):

        
        create_embedding(pdf)


        if(st.sidebar.button("create new chat")):
            st.session_state["messages"] = [
                    {"role": "assistant", "content": "Hello! How can I help you today?"}
                ]
            st.rerun()
    
        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                {"role": "assistant", "content": "Hello! How can I help you today?"}
            ]
        
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg['content'])
        
        input_placeholder = st.empty()   
        button_placeholder = st.empty()   
        # user_input = st.text_input("Type your message:", key="user_input")
        # send_button=st.button("Send")
        user_input = input_placeholder.text_input("Type your message:", key="user_input")
        send_button = button_placeholder.button("Send")

        if send_button and user_input:

            input_placeholder.empty()   
            button_placeholder.empty()  

            st.session_state["messages"].append({"role": "human", "content": user_input})
            
            with st.chat_message("human"):
                st.write(user_input)
            


            placeholder = st.empty()
            response = ""
            # response = create_final_message_state(st.session_state['messages'])

            for chunk in create_final_message_state(st.session_state["messages"]):
                response += chunk.content
                placeholder.markdown(response)

            st.session_state['messages'].append({"role": "assistant", "content": response})
            
            # with st.chat_message("assistant"):
            #     st.write(response)
            
            st.rerun()    







