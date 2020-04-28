FROM python:3.6

EXPOSE 5000

COPY nutrics_app /app/

WORKDIR /app

# COPY requirements.txt /app/
# COPY local.py /app/
# COPY env.py /app/
# COPY models.py /app/
# COPY resources.py /app/
# COPY run.py /app/
# COPY views.py /app/
# COPY nlp_resources/ /app/

RUN pip install -r requirements.txt

CMD FLASK_APP=run.py FLASK_RUN_PORT=5000 FLASK_DEBUG=1 FLASK_RUN_HOST=0.0.0.0 flask run