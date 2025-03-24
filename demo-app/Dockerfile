FROM python:3.12-slim-bullseye

WORKDIR /usr/src/app

#COPY ./requirements.txt ./
#RUN pip install -r requirements.txt

RUN pip install Flask==3.1.0
RUN pip install ibm_watsonx_ai==1.3.0
RUN pip install nltk==3.9.1
RUN pip install umap-learn==0.5.7
RUN pip install matplotlib==3.10.1
RUN pip install langchain-text-splitters==0.3.6
#RUN pip install sentence-transformers==3.4.1

COPY . .
EXPOSE 8080
ENV PORT=8080
ENV FLASK_APP=server.py
CMD [ "flask", "run", "--host", "0.0.0.0", "--port", "8080" ]
