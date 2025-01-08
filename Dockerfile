FROM python:3.8-slim

# We copy just the requirements.txt first to leverage Docker cache

WORKDIR /datastorage

# RUN useradd -ms /bin/bash admin

COPY ./requirements.txt /datastorage/requirements.txt

EXPOSE 8080

RUN pip install -r requirements.txt

COPY . .

# RUN touch record.log 
# RUN touch paths.txt

# RUN chown -R admin /datastorage
# RUN chown -R admin:admin /datastorage/
# RUN chmod -R a+rw /datastorage/record.log
# RUN chmod -R a+rw /datastorage/paths.txt
# USER admin

WORKDIR /datastorage/source

ENTRYPOINT [ "python" ]

CMD [ "datastorage.py" ]






