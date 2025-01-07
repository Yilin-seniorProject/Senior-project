# Senior-project
## Introduction

Senior project of drone for objecct detection on roads.
Team Number: 14
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

Ncnn inference: clone [ncnn](https://github.com/Tencent/ncnn.git) repositories and follow the example about [yolov5ncnn](https://www.wpgdadatong.com/blog/detail/75045). 
Using yolov7.cpp for inference, importing the **subprocess** module in Python is the easiest way to get the result.

## Model

Class: car, motorcycle and taxi (for pedestrains) 

## Deadlines

- Result Report Submission (Prof.): 17:00 114/01/08 (Wed.)
- Result Report Submission (CD): 17:00 114/01/13 (Mon.)

##　TODO

- Choose class name for motorcycle or scooter
- add drone position in front end for reference
- check coordi_transfer.py
- change the name of vechileType(1, 2, 3) ->(car, scooter, ...)