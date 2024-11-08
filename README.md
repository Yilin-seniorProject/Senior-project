# Senior-project
## Introduction

Senior project of drone  

## Regulations

### Commit Rule
Please follow the annotation rules provided at the following URL when writing comments:  
[git style](https://wadehuanglearning.blogspot.com/2019/05/commit-commit-commit-why-what-commit.html)

### Test files
If you have any test files, please named it "*filename_test*" and __DO NOT__ push to main branch.

## Data Transfer

### Refresh User Interface
Front end: request for **latitude**, **longitude**, and **vehicleType**.
back end: send the data for **ImageName**, **Latitude**, **Longitude**, and **ImageType** from database.db.

### Image Request
Front end: give **markerId** and request for **image_path**
back end: get **ImageName** by searching **ROWID** in database and send **image_path**

## Object Detection
Ncnn inference: clone [ncnn](https://github.com/Tencent/ncnn.git) repositories and follow the example about [yolov5ncnn](https://www.wpgdadatong.com/blog/detail/75045)
Using yolov7.cpp for inference, importing the **subprocess** module in Python is the easiest way to get the result.

## Model:
class: taxi, car, and motorcycle
