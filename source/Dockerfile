# Use an official Python runtime as a parent image
FROM python:3.7-slim
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
#RUN pip install --upgrade pip setuptools wheel
#RUN pip install pipwin && pipwin install pyaudio
# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 5000
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
