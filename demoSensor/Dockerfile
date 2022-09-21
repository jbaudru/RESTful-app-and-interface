FROM python:3.8

ADD demoAppSensor.py appInterface.py .

RUN pip install requests numpy tqdm schedule tensorflow pandas psutil h5py h5_to_json keras

CMD ["python", "./demoAppSensor.py"]