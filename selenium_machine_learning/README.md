Download openvino

download the relevent models.

`python /opt/intel/openvino_2019.3.376/deployment_tools/open_model_zoo/tools/downloader/downloader.py --name text-recognition-0012`

`python /opt/intel/openvino_2019.3.376/deployment_tools/open_model_zoo/tools/downloader/downloader.py --name text-detection-0004`

`python /opt/intel/openvino/deployment_tools/open_model_zoo/tools/downloader/downloader.py --name ssd_mobilenet_v2_coco`


To run unittests:

`$ python test_imgur.py`
